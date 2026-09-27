# Original source is the NCRB section table (ncrb.gov.in), via the UP Police PDF.

import re
import csv
import random
from collections import Counter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLineHorizontal

pdf_path = 'data/raw/BNS_IPC_Comparative.pdf'
output_csv = 'data/ipc_bns_mapping.csv'

def clean_text(text):
    text = re.sub(r'[\u2010\u2013\u2014\u2212\u00ad\ufffd]', '-', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_header_line(text):
    if not text: return True
    txt = text.strip()
    if re.search(r'Corresponding Section Table|New Addition|Bharatiya Nyaya Sanhita|Indian Penal Code|2023 \(BNS\)|1860 \(IPC\)|Note: For Reference', txt, re.IGNORECASE):
        return True
    
    if re.match(r'^(?:CHAPTER\s+[IVXLCDM\d]+|Chapter\s+[IVXLCDM\d]+)', txt, re.IGNORECASE):
        return True
    
    headers_patterns = [
        r'^OF\s+OFFENCES', r'^OF\s+CONTEMPTS', r'^OF\s+FALSE\s+EVIDENCE', r'^OF\s+THE\s+RECEIVING',
        r'^OF\s+FRAUDULENT', r'^OF\s+CRIMINAL', r'^OF\s+ATTEMPTS', r'^OF\s+HURT', r'^OF\s+MURDER',
        r'^OF\s+EXTORTION', r'^OF\s+ROBBERY', r'^OF\s+MISCHIEF', r'^OF\s+CHEATING', r'^OF\s+DEFAMATION',
        r'^SAFETY,\s+CONVENIENCE', r'^OF\s+WEIGHTS', r'^MEASURES\b', r'^OF\s+DEFINITIONS', r'^OF\s+PUNISHMENTS',
        r'^OF\s+KIDNAPPING', r'^OF\s+WRONGFUL', r'^OF\s+RAPE', r'^OF\s+UNNATURAL', r'^OF\s+MARRIAGE'
    ]
    for pat in headers_patterns:
        if re.search(pat, txt, re.IGNORECASE) and not re.search(r'\d', txt):
            return True

    return False

def is_bns_section_start(text):
    if not text: return False
    text = text.strip()
    if is_header_line(text): return False
    if re.match(r'^(?:Deleted|Omitted)\b', text, re.IGNORECASE): return True
    if re.match(r'^\d+[A-Z]*(?:\s*\(\d+[a-z]?\))*\s*[\.\-\)]', text): return True
    if re.match(r'^\d+[A-Z]*(?:\s*\(\d+[a-z]?\))+', text): return True
    return False

def is_ipc_section_start(text):
    if not text: return False
    text = text.strip()
    if is_header_line(text): return False
    if re.match(r'^(?:New\s+Sub-?\s*Section|New\s+Section|New|Deleted|Omitted)\b', text, re.IGNORECASE): return True
    if re.match(r'^\d+[A-Z]*(?:\s*\(\d+[a-z]?\))*\s*[\.\-\)]', text): return True
    if re.match(r'^\d+[A-Z]*(?:\s*\(\d+[a-z]?\))+', text): return True
    return False

def parse_comparative_pdf():
    raw_entries = []

    for page_idx, page_layout in enumerate(extract_pages(pdf_path)):
        page_num = page_idx + 1
        lines = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if isinstance(text_line, LTTextLineHorizontal):
                        text = text_line.get_text().strip()
                        if text:
                            x0, y0, x1, y1 = text_line.bbox
                            lines.append({'y0': y0, 'y1': y1, 'x0': x0, 'x1': x1, 'text': text})
        
        lines.sort(key=lambda l: -l['y0'])

        filtered = []
        for l in lines:
            txt = clean_text(l['text'])
            if is_header_line(txt):
                continue
            filtered.append(l)

        clusters = []
        for l in filtered:
            placed = False
            for c in clusters:
                avg_y = sum(item['y0'] for item in c) / len(c)
                if abs(l['y0'] - avg_y) < 10:
                    c.append(l)
                    placed = True
                    break
            if not placed:
                clusters.append([l])

        for c in clusters:
            c.sort(key=lambda item: item['x0'])
            bns_parts = [item['text'] for item in c if item['x0'] < 280]
            ipc_parts = [item['text'] for item in c if item['x0'] >= 280]
            
            bns_str = clean_text(" ".join(bns_parts))
            ipc_str = clean_text(" ".join(ipc_parts))

            if not bns_str and not ipc_str:
                continue

            raw_entries.append({
                'page': page_num,
                'bns_raw': bns_str,
                'ipc_raw': ipc_str,
            })

    grouped = []
    curr = None

    for item in raw_entries:
        bns = item['bns_raw']
        ipc = item['ipc_raw']
        page = item['page']

        is_bns = is_bns_section_start(bns)
        is_ipc = is_ipc_section_start(ipc)

        if is_bns or is_ipc or curr is None:
            if curr:
                grouped.append(curr)
            curr = {
                'page': page,
                'bns_parts': [bns] if bns else [],
                'ipc_parts': [ipc] if ipc else []
            }
        else:
            if bns: curr['bns_parts'].append(bns)
            if ipc: curr['ipc_parts'].append(ipc)

    if curr:
        grouped.append(curr)

    temp_rows = []
    failed_rows = []

    bns_sec_extractor = re.compile(r'^(Deleted|Omitted|\d+[A-Z]*(?:\s*\(\d+[a-z]?\))*)', re.IGNORECASE)
    ipc_sec_extractor = re.compile(r'^(New\s+Sub-?\s*Section|New\s+Section|New|Deleted|Omitted|\d+[A-Z]*)', re.IGNORECASE)

    bns_base_to_ipc = {}
    last_bns_sec = ""

    for entry in grouped:
        bns_text = clean_text(" ".join(entry['bns_parts']))
        ipc_text = clean_text(" ".join(entry['ipc_parts']))
        page = entry['page']

        if not bns_text and not ipc_text:
            continue

        bns_sec = ""
        bns_match = bns_sec_extractor.match(bns_text)
        if bns_match:
            bns_sec = bns_match.group(1).replace(" ", "")

        ipc_sec = ""
        ipc_match = ipc_sec_extractor.match(ipc_text)
        if ipc_match:
            ipc_sec = ipc_match.group(1).replace(" ", "")

        if not bns_sec and last_bns_sec and not is_bns_section_start(bns_text):
            bns_sec = last_bns_sec
        elif bns_sec:
            last_bns_sec = bns_sec

        bns_base = ""
        m_base = re.match(r'^(\d+)', bns_sec)
        if m_base:
            bns_base = m_base.group(1)

        if bns_base and ipc_sec and ipc_sec.lower() not in ['newsection', 'newsub-section', 'new', 'deleted', 'omitted']:
            if bns_base not in bns_base_to_ipc:
                bns_base_to_ipc[bns_base] = ipc_sec

        is_explicit_new = bool(re.search(r'^(New\s+Sub-?\s*Section|New\s+Section|New)\b', ipc_text, re.IGNORECASE))
        is_explicit_deleted = bool(re.search(r'^(Deleted|Omitted)\b', bns_text, re.IGNORECASE)) or bool(re.search(r'^(Deleted|Omitted)\b', ipc_text, re.IGNORECASE))

        subj_text = bns_text if is_explicit_new else (ipc_text if ipc_text else bns_text)
        subj_clean = re.sub(r'^(New\s+Sub-?\s*Section|New\s+Section|New|Deleted|Omitted|\d+[A-Z]*(?:\s*\(\d+[a-z]?\))*)[\.\s\-]*', '', subj_text, flags=re.IGNORECASE)
        subj_clean = re.sub(r'\s*\((?:Change|New Addition|Deleted)\)\s*$', '', subj_clean, flags=re.IGNORECASE).strip()
        subj_clean = subj_clean.rstrip('.').strip()
        subject = subj_clean

        relation = ""
        if is_explicit_new:
            relation = 'new_in_bns'
            ipc_sec = 'N/A'
        elif is_explicit_deleted:
            relation = 'omitted_from_ipc'
            if bns_sec.lower() in ['deleted', 'omitted']: bns_sec = 'Deleted'
            if ipc_sec.lower() in ['deleted', 'omitted']: ipc_sec = 'Deleted'

        if not bns_sec and not ipc_sec and not subject:
            failed_rows.append({'page': page, 'bns_raw': bns_text, 'ipc_raw': ipc_text})
            continue

        temp_rows.append({
            'ipc_section': ipc_sec,
            'bns_section': bns_sec,
            'bns_base_section': bns_base if bns_base else ('N/A' if bns_sec == 'Deleted' else bns_sec),
            'subject': subject,
            'relation': relation,
            'source_page': str(page),
            'source': 'pdf'
        })

    # Add BNS 103(2) (Mob Lynching - New in BNS) manually if not present
    has_103_2 = any(r['bns_section'] == '103(2)' for r in temp_rows)
    if not has_103_2:
        temp_rows.append({
            'ipc_section': 'N/A',
            'bns_section': '103(2)',
            'bns_base_section': '103',
            'subject': 'Murder by group of five or more on grounds of race, caste, community etc. (not in source PDF; added from BNS text)',
            'relation': 'new_in_bns',
            'source_page': 'manual',
            'source': 'manual'
        })

    ipc_counts = Counter()
    for r in temp_rows:
        if not r['ipc_section'] and r['relation'] not in ['new_in_bns', 'omitted_from_ipc']:
            b_base = r['bns_base_section']
            if b_base in bns_base_to_ipc:
                r['ipc_section'] = bns_base_to_ipc[b_base]
        
        if r['ipc_section'] and r['ipc_section'] not in ['N/A', 'Deleted']:
            ipc_counts[r['ipc_section']] += 1

    # Merge parent BNS section with first sub-section where PDF gives parent followed by sub-section
    parent_sub_changed_count = 0
    to_remove = set()
    for i in range(len(temp_rows) - 1):
        r1 = temp_rows[i]
        r2 = temp_rows[i+1]
        if r1['ipc_section'] and r1['ipc_section'] == r2['ipc_section'] and r1['ipc_section'] not in ['N/A', 'Deleted']:
            if r1['bns_base_section'] == r2['bns_base_section'] and r1['bns_section'] == r1['bns_base_section'] and '(' in r2['bns_section']:
                r2['subject'] = r1['subject'] if r1['subject'] else r2['subject']
                to_remove.add(i)
                parent_sub_changed_count += 1

    temp_rows = [r for idx, r in enumerate(temp_rows) if idx not in to_remove]
    print(f"Parent to sub-section merged rows: {parent_sub_changed_count}")

    ipc_distinct_bns = {}
    for r in temp_rows:
        ipc = r['ipc_section']
        bns = r['bns_section']
        if ipc and ipc not in ['N/A', 'Deleted']:
            if ipc not in ipc_distinct_bns:
                ipc_distinct_bns[ipc] = set()
            ipc_distinct_bns[ipc].add(bns)

    final_rows = []
    seen_rows = set()
    exact_duplicates_count = 0

    for r in temp_rows:
        rel = r['relation']
        ipc = r['ipc_section']

        if not rel:
            if ipc and ipc not in ['N/A', 'Deleted']:
                if len(ipc_distinct_bns.get(ipc, set())) > 1:
                    rel = 'split'
                else:
                    rel = 'direct'
            else:
                rel = 'direct'

        r['relation'] = rel

        if (r['bns_section'] in ['Deleted', ''] or not r['bns_section']) and (r['ipc_section'] in ['Deleted', ''] or not r['ipc_section']) and not r['subject']:
            continue
        if r['subject'].isupper() and len(r['subject']) > 5 and not r['bns_section'] and not r['ipc_section']:
            continue

        row_tuple = (r['ipc_section'], r['bns_section'], r['bns_base_section'], r['subject'], r['relation'], r['source_page'], r['source'])
        if row_tuple in seen_rows:
            exact_duplicates_count += 1
            continue
        seen_rows.add(row_tuple)

        final_rows.append(r)

    print(f"Removed {exact_duplicates_count} exact duplicate rows.")
    return final_rows, failed_rows

if __name__ == '__main__':
    rows, failed = parse_comparative_pdf()
    print(f"Total parsed unique rows: {len(rows)}")
    print(f"Failed rows: {len(failed)}")
    
    fieldnames = ['ipc_section', 'bns_section', 'bns_base_section', 'subject', 'relation', 'source_page', 'source']
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r[k] for k in fieldnames})

    print(f"CSV saved to {output_csv}")

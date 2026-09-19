from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from search_core import SearchEngine
from rag_core import generate_explanation, translate_to_english
from citations_core import find_related_cases
from pdf_core import extract_text_from_pdf, answer_question_about_document, summarize_document, extract_dates_and_deadlines
from dictionary_core import define_term

app = FastAPI(title="NyaayaSearch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = None

document_store = {}


@app.on_event("startup")
def load_engine():
    global engine
    engine = SearchEngine()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class DocumentQuestionRequest(BaseModel):
    document_id: str
    question: str


class DefineRequest(BaseModel):
    term: str


def attach_related_cases(results):
    for r in results:
        try:
            r["related_cases"] = find_related_cases(r["act_name"], r["section_number"])
        except Exception:
            r["related_cases"] = []
    return results


@app.get("/")
def root():
    return {"status": "NyaayaSearch API is running"}


@app.post("/search")
def search(request: SearchRequest):
    results = engine.search(request.query, top_k=request.top_k)
    results = attach_related_cases(results)
    return {"query": request.query, "results": results}


@app.post("/explain")
def explain(request: SearchRequest):
    search_query = translate_to_english(request.query)
    results = engine.search(search_query, top_k=request.top_k)
    results = attach_related_cases(results)
    explanation = generate_explanation(request.query, results)
    return {
        "query": request.query,
        "translated_query": search_query,
        "results": results,
        "explanation": explanation,
    }


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    file_bytes = await file.read()
    text = extract_text_from_pdf(file_bytes)

    document_id = file.filename + "_" + str(len(text))
    document_store[document_id] = text

    summary = summarize_document(text)
    dates = extract_dates_and_deadlines(text)

    return {
        "document_id": document_id,
        "filename": file.filename,
        "character_count": len(text),
        "summary": summary,
        "dates": dates,
    }


@app.post("/ask-document")
def ask_document(request: DocumentQuestionRequest):
    text = document_store.get(request.document_id)
    if not text:
        return {"error": "Document not found. Please upload it again."}

    answer = answer_question_about_document(text, request.question)
    return {"answer": answer}


@app.post("/define")
def define(request: DefineRequest):
    definition = define_term(request.term)
    return {"term": request.term, "definition": definition}

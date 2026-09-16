import requests
import xml.etree.ElementTree as ET

BUCKET_URL = "https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/"
OUTPUT_FILE = "data/case_law/raw/metadata_files.txt"

keys = []
continuation_token = None

while True:
    params = {"list-type": "2", "max-keys": "1000"}

    if continuation_token:
        params["continuation-token"] = continuation_token

    response = requests.get(BUCKET_URL, params=params, timeout=60)
    response.raise_for_status()

    root = ET.fromstring(response.text)

    for contents in root.findall("{http://s3.amazonaws.com/doc/2006-03-01/}Contents"):
        key = contents.find("{http://s3.amazonaws.com/doc/2006-03-01/}Key").text

        if key.lower().endswith(".parquet"):
            keys.append(key)

    truncated = root.find(
        "{http://s3.amazonaws.com/doc/2006-03-01/}IsTruncated"
    )

    if truncated is None or truncated.text.lower() != "true":
        break

    token = root.find(
        "{http://s3.amazonaws.com/doc/2006-03-01/}NextContinuationToken"
    )

    continuation_token = token.text

print("Parquet files found:", len(keys))
TestPath= r"data\case_law\processed\case_law_2015_2025.csv"
with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    for key in keys:
        file.write(key + "\n")

print("Saved file list to:", OUTPUT_FILE)
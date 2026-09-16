import requests

url = "https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/metadata/parquet/year=1950/metadata.parquet"

output = "data/case_law/raw/metadata_1950.parquet"

response = requests.get(url, timeout=120)
response.raise_for_status()

with open(output, "wb") as file:
    file.write(response.content)

print("Downloaded successfully")
print("Saved to:", output)
print("Size:", len(response.content), "bytes")
import requests
import sys

year = sys.argv[1]

url = (
    "https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/"
    f"metadata/parquet/year={year}/metadata.parquet"
)

output = f"data/case_law/raw/metadata_{year}.parquet"

response = requests.get(url, timeout=120)
response.raise_for_status()

with open(output, "wb") as file:
    file.write(response.content)

print(f"Downloaded {year} successfully")
print(f"Saved to: {output}")
print(f"Size: {len(response.content)} bytes")
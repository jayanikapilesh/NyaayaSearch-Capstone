import pandas as pd

print("Python is working!")
print("Pandas version:", pd.__version__)

data = {
    "law_id": ["LAW-C-001", "LAW-C-002"],
    "domain": ["Consumer", "Consumer"],
    "act_name": [
        "Consumer Protection Act, 2019",
        "Consumer Protection Act, 2019"
    ],
    "section_number": ["2", "10"]
}

df = pd.DataFrame(data)

print("\nOur first dataset:")
print(df)
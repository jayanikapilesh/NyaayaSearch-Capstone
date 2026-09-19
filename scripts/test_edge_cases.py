import requests

# Test 1: very long query
long_query = "landlord " * 300
r1 = requests.post("http://127.0.0.1:8000/search", json={"query": long_query, "top_k": 5})
print("Long query:", r1.status_code)
if r1.status_code != 200:
    print("  Detail:", r1.json().get("detail", "")[:150])

# Test 2: special characters / injection-like input
special_query = "landlord said \"pay now\" or leave; DROP TABLE users;-- \\ test"
r2 = requests.post("http://127.0.0.1:8000/search", json={"query": special_query, "top_k": 5})
print("Special chars:", r2.status_code)
if r2.status_code != 200:
    print("  Detail:", r2.json().get("detail", "")[:150])

# Test 3: gibberish/random text
r3 = requests.post("http://127.0.0.1:8000/search", json={"query": "asdkfj qwoeiru xzcvbn mnbvcxz", "top_k": 5})
print("Gibberish:", r3.status_code)
if r3.status_code != 200:
    print("  Detail:", r3.json().get("detail", "")[:150])

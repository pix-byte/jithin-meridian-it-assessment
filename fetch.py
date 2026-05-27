import requests
import hashlib
import json
import base64

BASE_URL = "https://ca-seassessment-api-dev.happywater-190f264d.northcentralus.azurecontainerapps.io"   # replace with real URL
API_KEY = "sa_1bbe5f31a5a510a6066980061d4a605700a976aed78d215acdf4c0d1868a672b"    # replace with real key

headers = {"Authorization": f"Bearer {API_KEY}"}

all_data = []
raw_pages = []
page = 1

while True:
    response = requests.get(
        f"{BASE_URL}/api/v1/dataset",
        headers=headers,
        params={"page": page, "page_size": 100}
    )
    raw_pages.append(response.text)
    body = response.json()
    records = body.get("data", [])
    all_data.extend(records)
    if not body.get("has_more", False):
        break
    page += 1

print(f"✅ Total records: {len(all_data)}")

# Approach 1: SHA-256 of all base64 strings concatenated directly
concat_raw = "".join(all_data).encode("utf-8")
print(f"\nApproach 1 (concat strings): {hashlib.sha256(concat_raw).hexdigest()}")

# Approach 2: SHA-256 of each decoded base64 bytes concatenated
decoded_bytes = b"".join(base64.b64decode(s) for s in all_data)
print(f"Approach 2 (decoded bytes):  {hashlib.sha256(decoded_bytes).hexdigest()}")

# Approach 3: SHA-256 of newline-joined strings
newline_joined = "\n".join(all_data).encode("utf-8")
print(f"Approach 3 (newline joined): {hashlib.sha256(newline_joined).hexdigest()}")

# Approach 4: SHA-256 of raw page bodies concatenated
all_raw = "".join(raw_pages).encode("utf-8")
print(f"Approach 4 (raw responses):  {hashlib.sha256(all_raw).hexdigest()}")

# Approach 5: SHA-256 of JSON array with default spacing
standard_json = json.dumps(all_data).encode("utf-8")
print(f"Approach 5 (standard JSON):  {hashlib.sha256(standard_json).hexdigest()}")

# Approach 6: MD5 of decoded bytes
print(f"\nApproach 2 MD5 (decoded):    {hashlib.md5(decoded_bytes).hexdigest()}")
print(f"Approach 1 MD5 (concat):     {hashlib.md5(concat_raw).hexdigest()}")


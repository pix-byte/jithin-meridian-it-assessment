from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64, hashlib, json

PRIVATE_KEY_PEM = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDJ/KnOOewo9m3o
faGtmMNotvtTiMIwMctzf7HFNstxfGdyvQEV2lw5YXJUswDlm00INuYa1HZj4fZg
pYrZqhc8/FRYkn2DfdgnXX5s6dOVZ2PH+NoS9UM2pi+Ys8qR7tu+kmkMskLq+dYK
uzHzANVkxe4oeqDshs85e0xWE8nLcO3dlOoWTZRfvsdVbatqeDPSapgyLdLqnyXJ
Ab7eblSFSps8Ka/vbe2MzP7T6AWuzssRDfzeT3FzU0bQ4JJZZ0EdWsBhTBvMEETe
L3AN7LrF5aV+r9YQboEP7PDi7pFZyaJ5Vkc7+0DF3kBLfuwiioKLuXBroLcyM68G
tO4jYkTtAgMBAAECggEACMvOAUMYe7gvlR5TeiHa8KZ3T233Nu4UNBVtgm8ecPS/
9IkykOcPeRg7SGD7OwSGWEM7xhNWjIb8mbzbzRrRJEDA05KdkKpcTWqO5ONR6YG1
ILI/nO+9W5XlILtDqRND0orBtGHW9DCpF5KLXE+++0J7WpvsgiBkydYKvvzhntBa
XCEYNEdH1tArlw11JGUClG/IkM3MHjplarnIdTDvh/Njj6aiZkImqhh1kuq/ZtVR
sm2xi+jZmH7xgT7cdkAgAIbd0B86Fnllj4VuhG1poGt6BHXoJzoIAyVFGi5+Poz6
E9V/hfwsT4j9nFOdUafyvoRqTuHmsq3uw1IdFRvTQQKBgQDoRRLs40342MoN1azI
zZ208h9t9jF0hE93zhSonox8Op7srvlcbv9D/bnDoMM91oBrjXZ31SLjg1hwNBZQ
eEvJW0XEAkTKfL+gcMO+lxrXUjrCS3iGg5UI0uh8w1MTdQR2/8h7ODilM09a7otZ
I+B+24AlmWAuOmzrrGPhDTC+2QKBgQDen42etor9HGSh42eHIiHO795cO8YbqVwX
AaK102a2qjT27000YshHOh6QHFTUnqeqWGlqszUHzpBGuAaPo1eLExd3h0y5vvJG
sx4CvmfcHI+Uc0SH9WvtGY+kyhI28CRfm1GTuvO8bao9sBT5URK/Hek0/3ECjBTZ
2CzG1SuSNQKBgQCeY7QjLGJYhuVKh+Ka0HRyFwZNwyw4a52RckvuLKhactM7TZqo
aNzT7asG95MMkUDjlwUpdIOlKEVfxnVNDKuJtR8fKfjlKCq46wzg5EQef2moYzTe
bc5sxP5bTgtR4mNYDtcVB+LA7Pt5Y+BMukV13JNHkI7hF2B9WgKGTqtmCQKBgA81
PRpzg+kokGNSwpbDqSWW00zftHfdSPI1ZWUgbOrbk8Suskp62Q2slbvog48Gy5Ni
eMkWNvAylz6Ngb08PlW81ySONJqXxbs4rzsmwLeTp+dPPIZBKL9IuLxcJYRlQUba
uGbsJYxgvXl7VuN1O1+c7np1XMX8xcvf7acjltdlAoGBAIxTWbSLGjpwJtpndVUg
/peluC11+geGcPTXdequKTIgMFibYKvpL/iMcxMjdDVCI9s7ohtWjMRqymd2cLr0
rKombFcbU0QIYynOOvpTlWNZwGScfvaaF0ap/lKF2SvgBpnDUJMRwGri6MutQFAZ
ymPIBSx6fxsD5hqT8ja4YAIY
-----END PRIVATE KEY-----"""

# Load private key
private_key = serialization.load_pem_private_key(
    PRIVATE_KEY_PEM.strip().encode(),
    password=None
)

# Load dataset
with open("dataset.json", "r") as f:
    all_data = json.load(f)

decrypted_records = []
failed = 0

for i, record in enumerate(all_data):
    ciphertext = base64.b64decode(record)
    
    # Try OAEP with SHA-256
    for pad in [
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()), algorithm=hashes.SHA1(), label=None),
        padding.PKCS1v15()
    ]:
        try:
            plaintext = private_key.decrypt(ciphertext, pad)
            decrypted_records.append(plaintext)
            break
        except Exception:
            continue
    else:
        failed += 1
        decrypted_records.append(b"")

print(f"✅ Decrypted: {len(decrypted_records) - failed}/500")
print(f"❌ Failed: {failed}")

# Show first 5 decrypted records
print("\n--- First 5 Decrypted Records ---")
for i in range(5):
    try:
        print(f"Record {i}: {decrypted_records[i].decode('utf-8', errors='replace')}")
    except:
        print(f"Record {i}: {decrypted_records[i]}")

# Compute Layer 2 hash
all_decrypted_bytes = b"".join(decrypted_records)
sha256_hash = hashlib.sha256(all_decrypted_bytes).hexdigest()
print(f"\n🔑 SHA-256 of all decrypted bytes: {sha256_hash}")

# Save decrypted data
with open("decrypted.json", "w") as f:
    json.dump([r.decode('utf-8', errors='replace') for r in decrypted_records], f, indent=2)
print("✅ Saved to decrypted.json")


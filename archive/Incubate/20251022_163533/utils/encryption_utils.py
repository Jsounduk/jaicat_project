# utils/encryption_utils.py

import json
from cryptography.fernet import Fernet

key = Fernet.generate_key()  # Load this from secure file in real use
cipher = Fernet(key)

def save_encrypted_json(filepath, data):
    raw = json.dumps(data).encode()
    encrypted = cipher.encrypt(raw)
    with open(filepath, "wb") as f:
        f.write(encrypted)

def load_encrypted_json(filepath):
    with open(filepath, "rb") as f:
        encrypted = f.read()
    return json.loads(cipher.decrypt(encrypted))


from cryptography.fernet import Fernet
import json

KEY = b'YOUR_32_BYTE_KEY=='  # Replace with actual secure key

def encrypt_log(data, out_file):
    fernet = Fernet(KEY)
    encrypted = fernet.encrypt(json.dumps(data).encode())
    with open(out_file, "wb") as f:
        f.write(encrypted)
from cryptography.fernet import Fernet
import json

KEY = b'YOUR_32_BYTE_KEY=='

def encrypt_log(data, out_file):
    fernet = Fernet(KEY)
    encrypted = fernet.encrypt(json.dumps(data).encode())
    with open(out_file, "wb") as f:
        f.write(encrypted)
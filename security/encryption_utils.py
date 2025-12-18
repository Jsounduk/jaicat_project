# security/encryption_utils.py
"""
Jaicat encryption helpers (Fernet + friendly JSON loaders).

- If JAICAT_SECRET is set (urlsafe base64 Fernet key) we use it directly.
- If a plain password is passed instead of a Fernet key, we derive a key
  with PBKDF2-HMAC(SHA256) using JAICAT_SALT (or a built-in default).
- load_encrypted_json() will gracefully fall back to plaintext JSON if the
  file isn’t encrypted. That keeps older files working.

Requires: cryptography
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Optional, Union

# cryptography is optional at import time, but most functions need it.
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # type: ignore
    from cryptography.hazmat.primitives import hashes  # type: ignore
    from cryptography.hazmat.backends import default_backend  # type: ignore
    from cryptography.fernet import Fernet, InvalidToken  # type: ignore
    _HAS_CRYPTO = True
except Exception:
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore
    _HAS_CRYPTO = False


# -------- key & cipher helpers --------

_DEF_SALT = b"jaicat-default-salt-v1"  # okay for non-critical data; override via env

def _is_fernet_key(s: str) -> bool:
    """Heuristic: Fernet keys are urlsafe base64 of 32 bytes -> ~44 chars."""
    try:
        raw = base64.urlsafe_b64decode(s.encode("utf-8"))
        return len(raw) == 32
    except Exception:
        return False

def _derive_fernet_key_from_password(password: str, salt: bytes) -> bytes:
    """Derive a 32-byte key from a password, then make it Fernet-safe (urlsafe base64)."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend(),
    )
    key = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)

def _resolve_salt() -> bytes:
    env_salt = os.getenv("JAICAT_SALT", "").encode("utf-8")
    if env_salt:
        # if user provided raw salt, use it; if they pasted b64, also fine
        try:
            return base64.urlsafe_b64decode(env_salt)
        except Exception:
            return env_salt
    return _DEF_SALT

def get_cipher(key_or_password: Optional[str] = None) -> Optional[Fernet]:
    """
    Returns a Fernet cipher or None if cryptography isnt available.

    Order of precedence:
      1) explicit key_or_password parameter
      2) env JAICAT_SECRET
      3) None (no cipher)
    If the selected value isn’t a Fernet key, we derive one with PBKDF2.
    """
    if not _HAS_CRYPTO:
        return None

    secret = (key_or_password or os.getenv("JAICAT_SECRET", "")).strip()
    if not secret:
        return None

    if _is_fernet_key(secret):
        key = secret.encode("utf-8")
    else:
        key = _derive_fernet_key_from_password(secret, _resolve_salt())

    try:
        return Fernet(key)
    except Exception:
        return None


# -------- string encryption --------

def encrypt_str(plaintext: str, key_or_password: Optional[str] = None) -> str:
    """
    Encrypt a string with Fernet. Raises RuntimeError if crypto is unavailable.
    """
    cipher = get_cipher(key_or_password)
    if cipher is None:
        raise RuntimeError("cryptography not available or no key provided (set JAICAT_SECRET or pass a password).")
    token = cipher.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")

def decrypt_str(token: str, key_or_password: Optional[str] = None, *, strict: bool = False) -> str:
    """
    Decrypt a Fernet token. If decryption fails:
      - strict=True  -> raise
      - strict=False -> return the original string (assume plaintext)
    """
    cipher = get_cipher(key_or_password)
    if cipher is None:
        return token if not strict else (_ for _ in ()).throw(RuntimeError("No cipher available"))
    try:
        return cipher.decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        if strict:
            raise
        return token
    except Exception:
        if strict:
            raise
        return token


# -------- JSON convenience --------

def load_json_plain(path: Union[str, Path], default: Any = None) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json_plain(path: Union[str, Path], data: Any) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_encrypted_json(path: Union[str, Path], data: Any, key_or_password: Optional[str] = None) -> None:
    """
    Encrypts the JSON serialization of `data` and writes a small envelope:
      { "__enc__": "fernet", "data": "<token>" }
    """
    cipher = get_cipher(key_or_password)
    if cipher is None:
        # no crypto → save plaintext to avoid data loss
        save_json_plain(path, data)
        return
    raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
    token = cipher.encrypt(raw).decode("utf-8")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"__enc__": "fernet", "data": token}, f)

def load_encrypted_json(path: Union[str, Path], default: Any = None, key_or_password: Optional[str] = None) -> Any:
    """
    Loads JSON that may be:
      - plaintext JSON
      - envelope {"__enc__":"fernet","data":"<token>"}
      - raw Fernet token of a JSON string

    If decryption fails or no crypto, we gracefully fall back to plaintext load.
    """
    p = Path(path)
    if not p.exists():
        return default

    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return default

    # 1) envelope?
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and obj.get("__enc__") == "fernet" and "data" in obj:
            token = obj["data"]
            try:
                decrypted = decrypt_str(token, key_or_password=key_or_password, strict=True)
                return json.loads(decrypted)
            except Exception:
                # fall back to default if decryption failed
                return default
        # 2) looks like regular JSON plaintext
        return obj
    except Exception:
        # 3) maybe the file is just a raw token
        try:
            decrypted = decrypt_str(text.strip(), key_or_password=key_or_password, strict=True)
            return json.loads(decrypted)
        except Exception:
            # 4) last resort: nothing worked
            return default


# -------- convenience / compatibility aliases (legacy names) --------

# some older code may import these names:
encrypt_data = encrypt_str
decrypt_data = decrypt_str
load_secure_json = load_encrypted_json
save_secure_json = save_encrypted_json

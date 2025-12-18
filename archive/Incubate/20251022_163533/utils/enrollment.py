# utils/enrollment.py
from __future__ import annotations
import os, json
from typing import Optional

PROJECT_ROOT = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
ENROLL_DIR = os.path.join(PROJECT_ROOT, "enrollment_json")

def ensure_enroll_dir():
    os.makedirs(ENROLL_DIR, exist_ok=True)

def safe_username(username: Optional[str]) -> str:
    return username or "Jay"

def enrollment_path(username: Optional[str]) -> str:
    ensure_enroll_dir()
    user = safe_username(username)
    return os.path.join(ENROLL_DIR, f"{user}.json")

def load_enrollment(username: Optional[str]) -> dict:
    path = enrollment_path(username)
    if not os.path.exists(path):
        return {"name": safe_username(username), "admin": (safe_username(username).lower() == "jay")}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_enrollment(username: Optional[str], data: dict):
    path = enrollment_path(username)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

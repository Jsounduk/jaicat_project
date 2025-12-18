# services/memory.py

import json
from pathlib import Path

MEMORY_FILE = Path("data/memory.json")

def load_memory():
    if not MEMORY_FILE.exists():
        return {}
    with open(MEMORY_FILE) as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user_memory(name):
    memory = load_memory()
    return memory["users"].get(name, {})

def update_user_memory(name, key, value):
    memory = load_memory()
    if name not in memory["users"]:
        memory["users"][name] = {}
    memory["users"][name][key] = value
    save_memory(memory)

import json
import os

def load_user_data():
    username = os.getenv("DEFAULT_USER", "default_user")
    path = f"jaicat_project/enrollment_json/{username}.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[user_loader] Failed to load user file {path}: {e}")
        return {"name": username}

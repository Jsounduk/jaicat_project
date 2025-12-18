# services/media_management/media_search.py

import os
from security.encryption_utils import load_encrypted_json

def find_images_by_tag(tag):
    folder = "data/snapshots"
    matches = []

    for file in os.listdir(folder):
        if file.endswith(".json"):
            data = load_encrypted_json(os.path.join(folder, file))
            if tag in data["tags"]:
                matches.append(data["image"])

    return matches


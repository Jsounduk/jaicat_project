# ✅ region_recognition.py (Full working region clustering & similarity engine)
# Purpose: Allow Jaicat to learn what "Becky's breasts" look like by visual similarity

import os
import json
import numpy as np
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity

import torch
import clip

REGION_DB_PATH = "services/media_management/region_vectors.json"

# Load CLIP
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)


def load_region_database():
    if not os.path.exists(REGION_DB_PATH):
        return []
    try:
        with open(REGION_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load region DB: {e}")
        return []


def save_region_database(db):
    try:
        with open(REGION_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to save region DB: {e}")


def extract_region_vector(image_path, coords):
    try:
        image = Image.open(image_path).convert("RGB")
        cropped = image.crop(coords)
        input_tensor = preprocess(cropped).unsqueeze(0).to(device)
        with torch.no_grad():
            vector = model.encode_image(input_tensor)
        return vector.cpu().numpy()[0]
    except Exception as e:
        print(f"❌ Error extracting region vector: {e}")
        return None


def add_region_to_database(image_path, coords, tag=None):
    vec = extract_region_vector(image_path, coords)
    if vec is None:
        return False
    db = load_region_database()
    db.append({
        "image": image_path,
        "coords": coords,
        "vector": vec.tolist(),
        "tag": tag or ""
    })
    save_region_database(db)
    print(f"✅ Region added with tag: {tag or '(none)'}")
    return True


def search_similar_regions(vector, top_k=10, db=None):
    if db is None:
        db = load_region_database()
    if not db:
        return []

    vectors = np.array([entry["vector"] for entry in db])
    query = np.array(vector).reshape(1, -1)
    scores = cosine_similarity(query, vectors)[0]

    scored = [
        {**entry, "score": float(score)}
        for entry, score in zip(db, scores)
    ]
    return sorted(scored, key=lambda x: -x["score"])[:top_k]


def find_similar_to_region(image_path, coords, top_k=5):
    vec = extract_region_vector(image_path, coords)
    if vec is None:
        return []
    return search_similar_regions(vec, top_k=top_k)


# Example manual run
if __name__ == "__main__":
    test_image = "C:/Users/josh_/OneDrive/Pictures/Samsung Gallery/Dcim/Camera/20150612_030713000_iOS.jpg"
    test_coords = (200, 300, 480, 520)  # Example region: Becky's breasts

    print("🧠 Learning visual region...")
    add_region_to_database(test_image, test_coords, tag="Beckys breasts")

    print("🔍 Finding visually similar regions...")
    results = find_similar_to_region(test_image, test_coords, top_k=5)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['image']} | {r['tag']} | Similarity: {r['score']:.3f}")

# ✅ image_organizer_tag_sorter.py

import os
import time
import shutil
import tkinter as tk
from PIL import Image
import imagehash
import face_recognition
from tag_ai import generate_tags
from face_loader import load_known_faces
from tag_sorter_engine import TagSorter, log_to_machine_learning
from tag_learning_helper import add_image_to_tag_cluster
from tag_ui import manual_tag_editor

# CONFIG
SOURCE_FOLDER = r"C:\Users\josh_\OneDrive\Pictures\Samsung Gallery\Dcim\Camera"
PICTURES_ROOT = r"C:\Users\josh_\OneDrive\Pictures\Samsung Gallery\Pictures"
UNSORTED_ROOT = os.path.join(PICTURES_ROOT, "SORT", "uncategorized")
FACES_PATH = "services/media_management/faces"
LOG_PATH = "services/media_management/tag_learning_log.json"
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif")

known_encodings, known_names = load_known_faces(FACES_PATH)
tag_sorter = TagSorter()
tag_sorter.train_from_log(LOG_PATH)


def _ensure_local_and_open(image_path):
    for _ in range(3):
        try:
            with Image.open(image_path) as im:
                im.load()
            return Image.open(image_path)
        except:
            time.sleep(0.5)
    raise FileNotFoundError(image_path)


def check_duplicate(path1, path2):
    try:
        h1 = imagehash.average_hash(Image.open(path1))
        h2 = imagehash.average_hash(Image.open(path2))
        return h1 - h2 < 5
    except:
        return False


def process_image(image_path):
    file_name = os.path.basename(image_path)

    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        person = None
        for encoding in encodings:
            results = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
            if True in results:
                person = known_names[results.index(True)]
                break
    except:
        person = None

    auto_tags = generate_tags(image_path)
    if person and person not in auto_tags:
        auto_tags.insert(0, person)

    result = manual_tag_editor(
        image_path,
        auto_tags,
        tag_sorter.available_tags(),
        tag_sorter.resolve_destination_from_tags,
        _ensure_local_and_open,
        PICTURES_ROOT,
        UNSORTED_ROOT,
        True,
        log_to_machine_learning,
        add_image_to_tag_cluster,
        check_duplicate
    )


def run():
    if not os.path.isdir(SOURCE_FOLDER):
        print(f"❌ SOURCE_FOLDER not found: {SOURCE_FOLDER}")
        return

    files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith(IMAGE_EXTS)]
    for file in files:
        try:
            process_image(os.path.join(SOURCE_FOLDER, file))
        except Exception as e:
            print(f"⚠️ Failed on {file}: {e}")


if __name__ == "__main__":
    run()


# ✅ tag_learning_helper.py

import os
import json
CLUSTER_PATH = "services/media_management/tag_clusters.json"

def load_clusters():
    try:
        with open(CLUSTER_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_clusters(clusters):
    os.makedirs(os.path.dirname(CLUSTER_PATH), exist_ok=True)
    with open(CLUSTER_PATH, "w", encoding="utf-8") as f:
        json.dump(clusters, f, indent=2)

def add_image_to_tag_cluster(tag, image_path):
    tag = tag.lower().strip()
    clusters = load_clusters()
    clusters.setdefault(tag, []).append(image_path)
    save_clusters(clusters)


def get_confidence(tag):
    tag = tag.lower().strip()
    clusters = load_clusters()
    count = len(clusters.get(tag, []))
    if count >= 15:
        return "high"
    elif count >= 5:
        return "medium"
    elif count >= 1:
        return "low"
    return "none"


# ✅ tag_sorter_engine.py

import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
import os

LOG_PATH = "services/media_management/tag_learning_log.json"

class TagSorter:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = KNeighborsClassifier(n_neighbors=3)
        self.X, self.y = [], []
        self.trained = False

    def train_from_log(self, path):
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            try:
                row = json.loads(line)
                tags = " ".join(row.get("tags", []))
                self.X.append(tags)
                self.y.append(row.get("path"))
            except:
                pass
        if self.X and self.y:
            self.X_vect = self.vectorizer.fit_transform(self.X)
            self.classifier.fit(self.X_vect, self.y)
            self.trained = True

    def predict_folder(self, tags):
        if not self.trained:
            return None
        vect = self.vectorizer.transform([" ".join(tags)])
        return self.classifier.predict(vect)[0]

    def available_tags(self):
        return sorted(set(tag for row in self.X for tag in row.split()))


def log_to_machine_learning(path, tags):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        json.dump({"path": path, "tags": tags}, f)
        f.write("\n")


# ✅ tag_ai.py

def generate_tags(image_path):
    file_name = os.path.basename(image_path)
    name = file_name.lower()
    tags = []
    if "rose" in name:
        tags.append("Rose")
    if "erin" in name:
        tags.append("Erin")
    if "becky" in name:
        tags.append("Becky")
    if "lace" in name:
        tags.append("Lace")
    if "bum" in name:
        tags.append("Bum")
    if "boob" in name or "breast" in name:
        tags.append("Breasts")
    return tags
  
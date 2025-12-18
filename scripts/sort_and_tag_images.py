# scripts/sort_and_tag_images.py

import os
from services.media_management.auto_tagger import auto_tag_image

def sort_folder(folder):
    for file in os.listdir(folder):
        if file.endswith((".jpg", ".png")):
            full_path = os.path.join(folder, file)
            tags = auto_tag_image(full_path)
            print(f"Tagged {file} with: {tags}")

sort_folder("data/snapshots")

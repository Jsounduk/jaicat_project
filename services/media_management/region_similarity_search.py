# region_similarity_search.py
import json
import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

EMBEDDINGS_PATH = "services/media_management/region_embeddings.json"

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_similar(region_index, top_n=5):
    with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
        entries = json.load(f)
    base_entry = entries[region_index]
    base_emb = base_entry["embedding"]

    sims = []
    for idx, entry in enumerate(entries):
        if idx == region_index:
            continue
        sim = cosine_similarity(base_emb, entry["embedding"])
        sims.append((sim, idx, entry))
    sims.sort(reverse=True)  # highest sim first

    print(f"\nMost similar to: {base_entry['label']} in {base_entry['image']}")
    for sim, idx, entry in sims[:top_n]:
        print(f"{entry['label']:<20} | {entry['image']} | Similarity: {sim:.3f}")
    return sims[:top_n]

def show_regions(region_idx, similar_entries):
    with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
        entries = json.load(f)
    # Show base region
    base = entries[region_idx]
    base_img = Image.open(base["image"])
    base_crop = base_img.crop(base["coords"])
    images = [base_crop]
    titles = [f"Query: {base['label']}"]

    for sim, idx, entry in similar_entries:
        img = Image.open(entry["image"])
        crop = img.crop(entry["coords"])
        images.append(crop)
        titles.append(f"{entry['label']} ({sim:.2f})")
    
    # Show in grid
    fig, axes = plt.subplots(1, len(images), figsize=(4*len(images), 4))
    if len(images) == 1:
        axes = [axes]
    for ax, img, title in zip(axes, images, titles):
        ax.imshow(img)
        ax.set_title(title)
        ax.axis("off")
    plt.tight_layout()
    plt.show()

def find_similar_for_image(image_path, region_idx=0, top_n=5):
    # Find the index in embeddings.json corresponding to image_path and region_idx
    with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
        entries = json.load(f)
    image_regions = [i for i, e in enumerate(entries) if e["image"] == image_path]
    if not image_regions:
        raise Exception(f"No regions found for {image_path} in embeddings.")
    # Clamp region_idx
    region_list_idx = image_regions[region_idx] if region_idx < len(image_regions) else image_regions[0]
    similar = find_similar(region_list_idx, top_n)
    return similar

def show_region_matches(image_path, region_idx, similar_entries):
    # Show the query region and its matches visually
    with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
        entries = json.load(f)
    image_regions = [i for i, e in enumerate(entries) if e["image"] == image_path]
    region_list_idx = image_regions[region_idx] if region_idx < len(image_regions) else image_regions[0]
    show_regions(region_list_idx, similar_entries)


if __name__ == "__main__":
    region_idx = 0  # <-- change to your desired region index!
    top_n = 5
    similar = find_similar(region_idx, top_n=top_n)
    show_regions(region_idx, similar)

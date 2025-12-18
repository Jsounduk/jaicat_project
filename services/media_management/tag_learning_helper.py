import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog

CLUSTER_PATH = "services/media_management/tag_clusters.json"

def load_clusters():
    if not os.path.exists(CLUSTER_PATH):
        return {}
    try:
        with open(CLUSTER_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_clusters(clusters):
    os.makedirs(os.path.dirname(CLUSTER_PATH), exist_ok=True)
    with open(CLUSTER_PATH, "w", encoding="utf-8") as f:
        json.dump(clusters, f, indent=2)

def normalize_tag(tag):
    return tag.strip().lower().replace("_", " ").replace("-", " ")

def add_image_to_tag_cluster(tag: str, image_path: str):
    clusters = load_clusters()
    canonical = normalize_tag(tag)
    if canonical not in clusters:
        clusters[canonical] = {"examples": [], "count": 0}
    clusters[canonical]["examples"].append(image_path)
    clusters[canonical]["count"] += 1
    save_clusters(clusters)

def tag_confidence_score(tag: str) -> str:
    clusters = load_clusters()
    canonical = normalize_tag(tag)
    count = clusters.get(canonical, {}).get("count", 0)
    if count >= 15:
        return "high"
    elif count >= 5:
        return "medium"
    elif count >= 1:
        return "low"
    return "none"

def get_tag_confidence_label(tag: str) -> str:
    conf = tag_confidence_score(tag)
    if conf == "high":
        return "🟢 High"
    elif conf == "medium":
        return "🟠 Med"
    elif conf == "low":
        return "🔴 Low"
    return "⚪️ None"

def all_learned_tags():
    clusters = load_clusters()
    return sorted(clusters.keys())

def resolve_destination_from_tags(tags):
    clusters = load_clusters()
    if not tags:
        return "Unsorted"
    primary = normalize_tag(tags[0])
    if primary in clusters:
        return os.path.join("Sorted", primary.title())
    return os.path.join("Sorted", "Misc") + os.path.sep + primary.title()

def log_to_ml(image_path, tags):
    # Placeholder for ML integration
    pass

def teach_tag_examples(tag):
    """Ask user to select up to 3 more examples for a new tag and add to cluster."""
    root = tk.Tk()
    root.withdraw()  # Hide root window
    if messagebox.askyesno("Teach Jaicat?", f"Do you want to teach me more about '{tag}'?\n\nPick up to 3 similar images."):
        files = filedialog.askopenfilenames(
            title="Select up to 3 more examples",
            filetypes=[("Images", "*.jpg *.jpeg *.png")]
        )
        for f in files:
            add_image_to_tag_cluster(tag, f)
        messagebox.showinfo("Thank you!", f"✅ Learned {len(files)} examples for '{tag}'.")
    root.destroy()

def teach_tag_cluster(image_path, tag_to_teach):
    """Old style single-image teaching, keep for compatibility."""
    clusters = load_clusters()
    canonical = normalize_tag(tag_to_teach)
    if canonical not in clusters:
        clusters[canonical] = {"examples": [], "count": 0}

    def on_yes():
        clusters[canonical]["examples"].append(image_path)
        clusters[canonical]["count"] += 1
        save_clusters(clusters)
        messagebox.showinfo("Thank you", f"✅ I've learned a bit more about '{tag_to_teach}'!")
        popup.destroy()

    def on_no():
        popup.destroy()

    popup = tk.Tk()
    popup.title("Teach Me?")
    popup.geometry("460x220")
    popup.resizable(False, False)
    tk.Label(popup, text=f"You tagged this as ‘{tag_to_teach}’.\nWant to teach me what it looks like?", font=("Arial", 12)).pack(pady=30)
    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Yes, learn this", command=on_yes, width=18, bg="#1a73e8", fg="white").pack(side="left", padx=12)
    tk.Button(btn_frame, text="No thanks", command=on_no, width=14).pack(side="left", padx=12)
    popup.mainloop()

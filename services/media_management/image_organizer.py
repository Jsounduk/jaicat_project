import os
import shutil
from PIL import Image, ImageTk
import tkinter as tk
import imagehash
import face_recognition
from tag_ai import generate_tags
from face_loader import load_known_faces

SOURCE_FOLDER = r"C:\Users\josh_\OneDrive\Pictures\Samsung Gallery\SORT"
FACES_PATH = "services/media_management/faces"
TAG_DB_PATH = "services/media_management/tag_db.json"

known_encodings, known_names = load_known_faces(FACES_PATH)

def check_duplicate(path1, path2):
    try:
        h1 = imagehash.average_hash(Image.open(path1))
        h2 = imagehash.average_hash(Image.open(path2))
        return h1 - h2 < 5
    except:
        return False

def resolve_duplicate_ui(file1, file2):
    root = tk.Tk()
    root.title("Duplicate Detected")

    img1 = Image.open(file1).resize((300, 300))
    img2 = Image.open(file2).resize((300, 300))
    tk_img1 = ImageTk.PhotoImage(img1)
    tk_img2 = ImageTk.PhotoImage(img2)

    tk.Label(root, text=f"Existing:\n{file2}").pack()
    tk.Label(root, image=tk_img1).pack()
    tk.Label(root, text=f"New:\n{file1}").pack()
    tk.Label(root, image=tk_img2).pack()

    decision = {"action": None}
    def keep_existing(): decision["action"] = "keep"; root.destroy()
    def keep_new(): decision["action"] = "replace"; root.destroy()
    def rename(): decision["action"] = "rename"; root.destroy()

    tk.Button(root, text="Keep Existing", command=keep_existing).pack()
    tk.Button(root, text="Replace with New", command=keep_new).pack()
    tk.Button(root, text="Rename New", command=rename).pack()

    root.mainloop()
    return decision["action"]

def manual_tag_editor(image_path, auto_tags):
    root = tk.Tk()
    root.title("Edit Tags")

    img = Image.open(image_path)
    img.thumbnail((300, 300))
    photo = ImageTk.PhotoImage(img)

    tk.Label(root, image=photo).pack()
    tk.Label(root, text="Edit Tags (comma-separated):").pack()

    entry = tk.Entry(root, width=100)
    entry.insert(0, ', '.join(auto_tags))
    entry.pack()

    final_tags = {"tags": None}
    def save_tags():
        final_tags["tags"] = [tag.strip() for tag in entry.get().split(',') if tag.strip()]
        root.destroy()

    tk.Button(root, text="Save & Continue", command=save_tags).pack()
    root.mainloop()

    return final_tags["tags"]

def process_image(image_path):
    file_name = os.path.basename(image_path)
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    matched_person = None
    for encoding in encodings:
        results = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
        if True in results:
            matched_person = known_names[results.index(True)]
            break

    auto_tags = generate_tags(image_path)
    if not auto_tags or auto_tags == ["misc"]:
        print("ðŸ” Auto-tag returned 'misc' â€” opening manual tag editor...")
        tags = manual_tag_editor(image_path, [matched_person] if matched_person else [])
    else:
        tags = manual_tag_editor(image_path, [matched_person] + auto_tags if matched_person else auto_tags)

    if not tags:
        print("â­ï¸ Skipping - no tags.")
        return

    dest_folder = os.path.join(SOURCE_FOLDER, *tags)
    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, file_name)

    if os.path.exists(dest_path) and check_duplicate(image_path, dest_path):
        action = resolve_duplicate_ui(image_path, dest_path)
        if action == "keep":
            return
        elif action == "replace":
            os.remove(dest_path)
        elif action == "rename":
            name, ext = os.path.splitext(file_name)
            dest_path = os.path.join(dest_folder, f"{name}_new{ext}")

    shutil.move(image_path, dest_path)
    print(f"âœ… Moved to {dest_path}")

def run():
    for file in os.listdir(SOURCE_FOLDER):
        full_path = os.path.join(SOURCE_FOLDER, file)
        if os.path.isfile(full_path) and file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            process_image(full_path)

if __name__ == "__main__":
    run()

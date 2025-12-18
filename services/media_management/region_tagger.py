import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from tag_learning_helper import add_image_to_tag_cluster
from media_management.body_part_detector import detect_body_part
from services.media_management.yolo_pose import detect_pose
from services.media_management.clothing_and_pose_detector import detect_clothing, detect_pose

# If you use face_loader: from face_loader import load_known_faces

SAVE_PATH = "services/media_management/region_tag_data.json"
# FACES_PATH = "services/media_management/faces"

class RegionTagger:
    def __init__(self, image_path, tag_suggestions=None):
        self.root = tk.Tk()
        self.root.title("Jaicat — Region Tagging")
        self.root.geometry("1000x800")
        self.image_path = image_path
        self._orig_img = Image.open(image_path)
        self.tk_image = None

        self.tag_suggestions = tag_suggestions or ["Rose", "Erin", "Becky", "Breasts", "Bum", "Lace"]

        self.boxes = []
        self.current_box = None
        self.start_x = None
        self.start_y = None

        self.selected_folder = tk.StringVar()
        self.sub_tag = tk.StringVar()

        self.setup_ui()
        self.root.mainloop()

    def setup_ui(self):
        # Canvas with dynamic resizing
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, pady=10)
        self.tk_image = None
        self.draw_image()

        self.canvas.bind("<Configure>", self.redraw_image)
        self.canvas.bind("<ButtonPress-1>", self.on_start_box)
        self.canvas.bind("<B1-Motion>", self.on_draw_box)
        self.canvas.bind("<ButtonRelease-1>", self.on_finish_box)

        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=5)
        tk.Label(folder_frame, text="Folder Tag:").pack(side="left")
        folder_dropdown = ttk.Combobox(folder_frame, textvariable=self.selected_folder, values=self.tag_suggestions, width=30)
        folder_dropdown.pack(side="left")
        folder_dropdown.set(self.tag_suggestions[0])

        tk.Label(folder_frame, text="Sub-Tag:").pack(side="left", padx=10)
        sub_tag_entry = ttk.Entry(folder_frame, textvariable=self.sub_tag, width=30)
        sub_tag_entry.pack(side="left")

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="✅ Save & Next", command=self.save_and_next, bg="#4CAF50", fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="⏭️ Skip", command=self.skip_image).pack(side="left", padx=10)

    def draw_image(self):
        if not self._orig_img:
            return
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            # Canvas too small, wait and try again
            self.root.after(50, self.draw_image)
            return
        img = self._orig_img.copy()
        if hasattr(Image, "Resampling"):
            img.thumbnail((w, h), Image.Resampling.LANCZOS)
        else:
            img.thumbnail((w, h), Image.ANTIALIAS)
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(w // 2, h // 2, anchor="center", image=self.tk_image)
        # Draw all previous boxes
        for box in self.boxes:
            x0, y0, x1, y1 = box["coords"]
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=2)
        print(f"Drawn image at size {w}x{h}")

    def redraw_image(self, event=None):
        self.draw_image()

    def on_start_box(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_box = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", width=2)

    def on_draw_box(self, event):
        if self.current_box:
            self.canvas.coords(self.current_box, self.start_x, self.start_y, event.x, event.y)

    def on_finish_box(self, event):
        x0, y0, x1, y1 = self.canvas.coords(self.current_box)
        self.prompt_tag_for_box(self.current_box, int(x0), int(y0), int(x1), int(y1))

    def prompt_tag_for_box(self, box_id, x0, y0, x1, y1):
        # DeepFashion clothing auto-detect
        clothing_found = detect_clothing(self.image_path, region=(x0, y0, x1, y1))
        clothing_tags = [c["label"] for c in clothing_found] if clothing_found else []
        
        # Pose/body part detection (optional: can be used to suggest "leg", "waist" etc)
        pose_points = detect_pose(self.image_path, region=(x0, y0, x1, y1))
        pose_tag = ""
        if pose_points:
            # Example: if keypoints present, suggest e.g. "ankle", "waist", "shoulder"
            pose_tag = "body part"
            # You can improve this to analyze which point is most centered

        # Build suggestions
        suggestions = []
        if clothing_tags:
            suggestions += clothing_tags
        if pose_tag:
            suggestions.append(pose_tag)
        suggestions += self.tag_suggestions  # Existing user/cluster tags

        # Remove duplicates
        suggestions = list(dict.fromkeys(suggestions))

        popup = tk.Toplevel(self)
        popup.title("Assign Tag")
        var = tk.StringVar(value=suggestions[0] if suggestions else "")
        cb = ttk.Combobox(popup, textvariable=var, values=suggestions, width=25)
        cb.pack(padx=10, pady=10)
        cb.set(var.get())

        def save_tag():
            tag = var.get()
            region = {
                "box_id": box_id,
                "coords": (x0, y0, x1, y1),
                "tag": tag,
            }
            self.boxes.append(region)
            add_image_to_tag_cluster(tag, self.image_path)
            popup.destroy()

        tk.Button(popup, text="OK", command=save_tag).pack(pady=5)


    # --- Optional: highlight body part in UI (later step)


    def save_and_next(self):
        all_data = {
            "image_path": self.image_path,
            "main_folder_tag": self.selected_folder.get(),
            "sub_tag": self.sub_tag.get(),
            "boxes": self.boxes
        }

        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        if os.path.exists(SAVE_PATH):
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                all_logs = json.load(f)
        else:
            all_logs = []

        all_logs.append(all_data)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(all_logs, f, indent=2)

        print(f"✅ Tagged: {self.image_path} — {len(self.boxes)} box(es)")
        self.root.destroy()

    def skip_image(self):
        print(f"⏭️ Skipped: {self.image_path}")
        self.root.destroy()

if __name__ == "__main__":
    sample = r"C:\\Users\\josh_\\OneDrive\\Pictures\\Samsung Gallery\\Dcim\\Camera\\20150612_030713000_iOS.jpg"
    RegionTagger(sample)

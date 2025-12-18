# ✅ FILE: tag_ui.py
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class TagUI:
    def __init__(self, image_path, auto_tags, AVAILABLE_TAGS, resolve_destination_from_tags, _ensure_local_and_open):
        self.image_path = image_path
        self.auto_tags = auto_tags
        self.AVAILABLE_TAGS = AVAILABLE_TAGS
        self.resolve_destination_from_tags = resolve_destination_from_tags
        self._ensure_local_and_open = _ensure_local_and_open

        self.selected_tags = auto_tags[:]
        self.subfolder = ""
        self.result = None

        self.root = tk.Tk()
        self.root.title("Jaicat — Manual Image Tagging")
        self.root.geometry("1000x860")

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill="both", expand=True)

        self.img_label = tk.Label(self.canvas)
        self.img_label.pack(pady=10)

        self.tag_dropdown = ttk.Combobox(self.canvas, values=self.AVAILABLE_TAGS, width=110)
        self.tag_dropdown.pack()
        self.tag_dropdown.bind("<Return>", self.add_suggested_tag)

        self.suggestion_frame = tk.Frame(self.canvas)
        self.suggestion_frame.pack(pady=4)

        self.tags_entry = tk.Entry(self.canvas, width=110)
        self.tags_entry.pack(pady=5)
        self.tags_entry.insert(0, ", ".join(auto_tags))
        self.tags_entry.bind("<KeyRelease>", lambda e: self.update_destination_label())

        self.sub_entry = tk.Entry(self.canvas, width=110)
        self.sub_entry.pack(pady=5)
        self.sub_entry.insert(0, "")
        self.sub_entry.bind("<KeyRelease>", lambda e: self.update_destination_label())

        self.dest_label = tk.Label(self.canvas, text="", fg="blue", wraplength=880)
        self.dest_label.pack(pady=6)

        btn_frame = tk.Frame(self.canvas)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="✅ Save", command=self.confirm).pack(side="left", padx=10)
        tk.Button(btn_frame, text="🗑️ Delete", command=self.delete_image).pack(side="left", padx=10)
        tk.Button(btn_frame, text="🔁 Uncategorized", command=self.mark_uncategorized).pack(side="left", padx=10)
        tk.Button(btn_frame, text="❌ Cancel", command=self.cancel).pack(side="left", padx=10)

        self.update_image()
        self.render_tag_suggestions()
        self.root.mainloop()

    def update_image(self):
        try:
            img = self._ensure_local_and_open(self.image_path)
            img.thumbnail((1400, 1400))
            tk_img = ImageTk.PhotoImage(img)
            self.img_label.configure(image=tk_img)
            self.img_label.image = tk_img
        except:
            self.img_label.configure(text="⚠️ Failed to load image")

    def render_tag_suggestions(self):
        for widget in self.suggestion_frame.winfo_children():
            widget.destroy()
        for tag in self.auto_tags[:12]:
            b = tk.Button(self.suggestion_frame, text=tag, command=lambda t=tag: self.add_tag(t))
            b.pack(side="left", padx=2)

    def add_tag(self, tag):
        tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        if tag not in tags:
            tags.append(tag)
            self.tags_entry.delete(0, tk.END)
            self.tags_entry.insert(0, ", ".join(tags))
            self.update_destination_label()

    def add_suggested_tag(self, _=None):
        tag = self.tag_dropdown.get().strip()
        if tag:
            self.add_tag(tag)
            self.tag_dropdown.set("")

    def update_destination_label(self):
        tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        sub = self.sub_entry.get().strip()
        base = self.resolve_destination_from_tags(tags)
        full = os.path.join(base, sub) if sub else base
        self.dest_label.config(text=f"Destination: {full}")

    def confirm(self):
        tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        sub = self.sub_entry.get().strip()
        self.result = {"tags": tags, "subfolder": sub}
        self.root.destroy()

    def delete_image(self):
        if messagebox.askyesno("Confirm Delete", "Really delete this image?"):
            self.result = "DELETE_FILE"
            self.root.destroy()

    def mark_uncategorized(self):
        self.result = "SORT_UNCATEGORIZED"
        self.root.destroy()

    def cancel(self):
        self.result = None
        self.root.destroy()


def manual_tag_editor(image_path, auto_tags, AVAILABLE_TAGS, resolve_destination_from_tags, _ensure_local_and_open):
    ui = TagUI(image_path, auto_tags, AVAILABLE_TAGS, resolve_destination_from_tags, _ensure_local_and_open)
    return ui.result

# services/media_management/find_similar_gui.py

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from region_recognition import find_similar_regions
import os

class SimilarRegionFinder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jaicat — Find More Like This")

        self.image_path = None
        self.region = None
        self.matches = []

        self.canvas = tk.Canvas(self.root, width=500, height=500, bg="white")
        self.canvas.pack(padx=10, pady=10)

        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack()

        tk.Button(self.btn_frame, text="Load Image", command=self.load_image).pack(side="left", padx=6)
        tk.Button(self.btn_frame, text="Draw Region", command=self.draw_mode).pack(side="left", padx=6)
        tk.Button(self.btn_frame, text="Find Similar", command=self.find_similar).pack(side="left", padx=6)

        self.match_frame = tk.Frame(self.root)
        self.match_frame.pack(pady=10)

        self.tk_img = None
        self.box_id = None
        self.start_x = None
        self.start_y = None
        self.canvas.bind("<Button-1>", self.start_box)
        self.canvas.bind("<B1-Motion>", self.resize_box)
        self.canvas.bind("<ButtonRelease-1>", self.finish_box)
        self.box_enabled = False

        self.root.mainloop()

    def load_image(self):
        path = filedialog.askopenfilename(title="Choose an image")
        if not path:
            return
        self.image_path = path
        img = Image.open(path)
        img.thumbnail((500, 500))
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.region = None

    def draw_mode(self):
        self.box_enabled = True
        messagebox.showinfo("Draw", "Click and drag to draw a region")

    def start_box(self, event):
        if not self.box_enabled:
            return
        self.start_x, self.start_y = event.x, event.y
        self.box_id = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", width=2)

    def resize_box(self, event):
        if self.box_id:
            self.canvas.coords(self.box_id, self.start_x, self.start_y, event.x, event.y)

    def finish_box(self, event):
        if not self.box_enabled:
            return
        x0, y0, x1, y1 = self.canvas.coords(self.box_id)
        self.region = (int(x0), int(y0), int(x1), int(y1))
        self.box_enabled = False

    def find_similar(self):
        if not self.image_path or not self.region:
            messagebox.showwarning("Missing", "Load an image and draw a region first.")
            return

        for widget in self.match_frame.winfo_children():
            widget.destroy()

        self.matches = find_similar_regions(self.image_path, self.region, top_k=6)
        for i, (score, match) in enumerate(self.matches):
            try:
                img = Image.open(match["path"]).convert("RGB")
                region = match["region"]
                img = img.crop(region)
                img.thumbnail((100, 100))
                thumb = ImageTk.PhotoImage(img)
                label = tk.Label(self.match_frame, image=thumb)
                label.image = thumb
                label.grid(row=0, column=i, padx=5)
                tk.Label(self.match_frame, text=f"{match['tag']}\n{score:.2f}").grid(row=1, column=i)
            except:
                pass

if __name__ == "__main__":
    SimilarRegionFinder()

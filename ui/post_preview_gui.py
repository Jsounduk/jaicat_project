# ui/post_preview_gui.py

import tkinter as tk
from PIL import ImageTk, Image

def show_post_preview(image_path, caption):
    root = tk.Tk()
    root.title("Jaicat Social Post Preview")

    img = Image.open(image_path)
    img = img.resize((400, 400))
    img_tk = ImageTk.PhotoImage(img)

    label = tk.Label(root, image=img_tk)
    label.pack()

    caption_box = tk.Text(root, height=5, width=50, font=("Arial", 12))
    caption_box.insert("1.0", caption)
    caption_box.pack()

    root.mainloop()

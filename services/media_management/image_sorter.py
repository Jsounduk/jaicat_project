from tkinter import Tk, Label, Button, Entry
from PIL import Image, ImageTk
import os, shutil, json
from tag_ai import generate_tags

TAG_DB_PATH = "services/media_management/tag_db.json"

class TagEditor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.root = Tk()
        self.root.title("Tag Image")
        self.root.geometry("800x600")

        # Load and display the image
        img = Image.open(image_path)
        img.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(img)
        self.image_label = Label(self.root, image=photo)
        self.image_label.image = photo
        self.image_label.pack()

        # Generate AI tags
        self.ai_tags = generate_tags(image_path)
        self.entry = Entry(self.root, width=100)
        self.entry.insert(0, ', '.join(self.ai_tags))
        self.entry.pack()

        self.save_button = Button(self.root, text="Save & Sort", command=self.save_and_sort)
        self.save_button.pack()

        self.root.mainloop()

    def save_and_sort(self):
        final_tags = [t.strip() for t in self.entry.get().split(',')]
        self.sort_image(final_tags)
        self.update_tag_db(final_tags)
        self.root.destroy()

    def sort_image(self, tags):
        for tag in tags:
            folder = os.path.join("sorted_images", tag)
            os.makedirs(folder, exist_ok=True)
            shutil.copy(self.image_path, folder)

    def update_tag_db(self, tags):
        try:
            with open(TAG_DB_PATH, 'r') as f:
                db = json.load(f)
        except:
            db = {}

        db[self.image_path] = tags
        with open(TAG_DB_PATH, 'w') as f:
            json.dump(db, f, indent=4)

# Example usage
if __name__ == "__main__":
    folder_path = "C:\\Users\\josh_\\OneDrive\\Pictures\\Screenshots"
    for fname in os.listdir(folder_path):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            TagEditor(os.path.join(folder_path, fname))

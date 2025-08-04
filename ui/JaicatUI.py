import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv
from PIL import Image, ImageTk
import cv2
from services.bluetooth_service import BluetoothService
from services.weather_service import WeatherService


class JaicatUI:
    def __init__(self, assistant):
        """Initialize the UI and connect it to the Jaicat assistant."""
        self.assistant = assistant  # Reference to the Jaicat assistant
        self.bluetooth_service = BluetoothService()

        # Set up the window
        self.window = tk.Tk()
        self.window.title("Jaicat - AI Assistant")
        self.window.geometry("1200x800")  # Set window size
        self.window.configure(bg="#2C3E50")  # Change background color

        self.create_widgets()
        self.window.after(200, self.load_face_image)  # Wait to ensure label exists

    def set_face(self, mood="happy"):
        """Change the assistant's face image based on mood."""
        mood_map = {
            "happy": "face_happy.png",
            "sad": "face_sad.png",
            "flirty": "face_flirty.png",
            "neutral": "face_neutral.png"
        }
        filename = mood_map.get(mood.lower(), "face_neutral.png")
        path = os.path.join(os.path.dirname(__file__), filename)

        if not os.path.exists(path):
            print(f"❌ Mood image '{filename}' not found. Reverting to default.")
            path = os.path.join(os.path.dirname(__file__), "default_image.png")

        try:
            self.face_image = Image.open(path)
            self.face_image_tk = ImageTk.PhotoImage(self.face_image)
            self.face_image_label.config(image=self.face_image_tk)
            self.face_image_label.image = self.face_image_tk  # Prevent garbage collection
        except Exception as e:
            print(f"Error displaying mood image: {e}")

    def load_face_image(self):
        self.set_face("happy")

    def create_widgets(self):
        """Set up the UI components like buttons, labels, input boxes, etc."""
        main_frame = tk.Frame(self.window, bg="#2C3E50")
        main_frame.pack(fill="both", expand=True)

        print("Creating Label to show the face image")
        self.face_image_label = tk.Label(main_frame)
        self.face_image_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        print("Creating Button to play a song via Spotify")
        self.play_button = tk.Button(
            main_frame,
            text="Play Music",
            command=lambda: self.assistant.command_processor.execute_command("play music", "Shape of You"),
            font=("Arial", 12),
            bg="#3498db",
            fg="white"
        )
        self.play_button.grid(row=1, column=0, padx=10, pady=10)

        print("Creating Calendar Widget")
        self.calendar_label = tk.Label(main_frame, text="Calendar", font=("Arial", 14), bg="#2C3E50", fg="white")
        self.calendar_label.grid(row=2, column=0, padx=10, pady=10)
        self.calendar = tk.Label(main_frame, text=self.assistant.calendar_service.get_current_date(), font=("Arial", 14), bg="#1ABC9C", fg="white")
        self.calendar.grid(row=3, column=0, padx=10, pady=10)

        print("Creating Weather Label")
        self.weather_label = tk.Label(main_frame, text="", font=("Arial", 14), bg="#1ABC9C", fg="white")
        self.weather_label.grid(row=0, column=1)

        print("Creating Circular Button for user input")
        self.input_button = tk.Button(main_frame, text="Text Input", command=self.show_input_box, font=("Arial", 12), bg="#E74C3C", fg="white")
        self.input_button.grid(row=4, column=0, padx=10, pady=10)

        print("Creating Hidden text input box")
        self.text_input = tk.Entry(main_frame, font=("Arial", 14))
        self.text_input.grid(row=5, column=0, padx=10, pady=10, columnspan=2)
        self.text_input.grid_remove()

        self.submit_button = tk.Button(main_frame, text="Submit", command=self.on_submit)
        self.submit_button.grid(row=6, column=0, padx=10, pady=10)

        self.response_box = tk.Text(main_frame, height=10, width=60, font=("Arial", 14))
        self.response_box.grid(row=7, column=0, padx=10, pady=10, columnspan=2)

        print("Creating Status Bar")
        self.status_bar = tk.Label(self.window, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 12))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def show_input_box(self):
        self.text_input.grid()

    def on_submit(self):
        user_input = self.text_input.get()
        try:
            self.assistant.process_user_input(user_input)
        except Exception as e:
            print(f"❌ Error processing input: {e}")

    def display_response(self, message):
        self.status_bar.config(text=message)
        self.response_box.insert(tk.END, f"Jaicat: {message}\n")
        self.response_box.see(tk.END)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    from main import Jaicat
    assistant = Jaicat()
    app = JaicatUI(assistant)
    assistant.ui = app
    app.run()

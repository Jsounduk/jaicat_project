import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

class DetectionViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("Saved Detections Viewer")
        self.master.geometry("600x400")

        self.detections_file = "computer_vision/detections.json"

        # Create a table to display detections
        self.tree = ttk.Treeview(self.master, columns=("License Plate", "Vehicle Model", "Confidence"), show="headings")
        self.tree.heading("License Plate", text="License Plate")
        self.tree.heading("Vehicle Model", text="Vehicle Model")
        self.tree.heading("Confidence", text="Confidence")
        self.tree.pack(fill="both", expand=True)

        # Button to load detections
        self.load_button = tk.Button(self.master, text="Load Detections", command=self.load_detections)
        self.load_button.pack(pady=10)

        # Export button
        self.export_button = tk.Button(self.master, text="Export Detections", command=self.export_detections)
        self.export_button.pack(pady=10)

    def load_detections(self):
        """Load and display saved detections from JSON file."""
        if not os.path.exists(self.detections_file):
            messagebox.showwarning("Warning", "No detections found.")
            return

        with open(self.detections_file, 'r') as file:
            detections = json.load(file)

        # Clear previous data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Display detections in the table
        for detection in detections:
            license_plate = detection.get("license_plate", "Unknown")
            vehicle_model = detection["vehicle_data"].get("model", "Unknown")
            confidence = detection["detected_cars"][0]["confidence"] if detection["detected_cars"] else "N/A"
            self.tree.insert("", "end", values=(license_plate, vehicle_model, confidence))

    def export_detections(self):
        """Export the detections to an external file."""
        export_path = "computer_vision/exported_detections.json"
        with open(self.detections_file, 'r') as file:
            detections = json.load(file)

        with open(export_path, 'w') as export_file:
            json.dump(detections, export_file, indent=4)

        messagebox.showinfo("Export", f"Detections exported to {export_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DetectionViewer(root)
    root.mainloop()

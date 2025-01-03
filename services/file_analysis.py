# services/file_analysis.py

import PyPDF2
from PIL import Image
import pytesseract
import os
import json
import csv


class FileAnalysisService:
    def __init__(self):
        pass

    def analyze_pdf(self, file_path):
        """Extract text from a PDF file."""
        if not file_path.lower().endswith('.pdf'):
            return "The provided file is not a PDF."

        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

        return text.strip() if text else "No text found in the PDF."

    def analyze_image(self, file_path):
        """Extract text from an image file using OCR."""
        if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return "The provided file is not an image."

        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip() if text else "No text found in the image."

    def analyze_text_file(self, file_path):
        """Read and return the content of a text file."""
        if not file_path.lower().endswith('.txt'):
            return "The provided file is not a text file."

        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()

    def file_analysis(self, file_path):
        """Determine the file type and perform analysis accordingly."""
        if os.path.exists(file_path):
            if file_path.lower().endswith('.pdf'):
                return self.analyze_pdf(file_path)
            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                return self.analyze_image(file_path)
            elif file_path.lower().endswith('.txt'):
                return self.analyze_text_file(file_path)
            else:
                return "Unsupported file type."
        else:
            return "File does not exist."
        
    def export_detections_to_csv(self, json_file, csv_file):
        try:
            with open(json_file, 'r') as jf:
                data = json.load(jf)

            with open(csv_file, 'w', newline='') as cf:
                writer = csv.writer(cf)
                writer.writerow(["License Plate", "Model", "Manufacturer"])

                for detection in data:
                    writer.writerow([detection['license_plate'], detection['vehicle_data']['model'], detection['vehicle_data']['manufacturer']])
            
            print(f"Data successfully exported to {csv_file}")

        except Exception as e:
            print(f"Error exporting data: {e}")

    def export_motorbike_detections(self, json_file, csv_file):
        try:
            with open(json_file, 'r') as jf:
                data = json.load(jf)

            with open(csv_file, 'w', newline='') as cf:
                writer = csv.writer(cf)
                writer.writerow(["License Plate", "Model", "Manufacturer"])

                for detection in data:
                    writer.writerow([detection['license_plate'], detection['vehicle_data']['model'], detection['vehicle_data']['manufacturer']])

            print(f"Motorbike detection data successfully exported to {csv_file}")
        except Exception as e:
            print(f"Error exporting motorbike data: {e}")

    def export_car_detections(self, json_file, csv_file):
        try:
            with open(json_file, 'r') as jf:
                data = json.load(jf)

            with open(csv_file, 'w', newline='') as cf:
                writer = csv.writer(cf)
                writer.writerow(["License Plate", "Model", "Manufacturer"])

                for detection in data:
                    writer.writerow([detection['license_plate'], detection['vehicle_data']['model'], detection['vehicle_data']['manufacturer']])

            print(f"Car detection data successfully exported to {csv_file}")
        except Exception as e:
            print(f"Error exporting car data: {e}")

    def export_vehicle_data(self, json_file, csv_file):
        try:
            with open(json_file, 'r') as jf:
                data = json.load(jf)

            with open(csv_file, 'w', newline='') as cf:
                writer = csv.writer(cf)
                writer.writerow(["License Plate", "Model", "Manufacturer"])

                for detection in data:
                    writer.writerow([detection['license_plate'], detection['vehicle_data']['model'], detection['vehicle_data']['manufacturer']])

            print(f"Vehicle data successfully exported to {csv_file}")
        except Exception as e:
            print(f"Error exporting vehicle data: {e}")

    def export_vehicle_data_to_csv(self, json_file, csv_file):
        try:
            with open(json_file, 'r') as jf:
                data = json.load(jf)

            with open(csv_file, 'w', newline='') as cf:
                writer = csv.writer(cf)
                writer.writerow(["License Plate", "Model", "Manufacturer"])

                for detection in data:
                    writer.writerow([detection['license_plate'], detection['vehicle_data']['model'], detection['vehicle_data']['manufacturer']])

            print(f"Vehicle data successfully exported to {csv_file}")
        except Exception as e:
            print(f"Error exporting vehicle data: {e}")

        return csv_file

    def export_motorbike_data_to_csv(self, json_file, csv_file):
        try:
            with open(json_file, 'r') as jf:
                data = json.load(jf)

            with open(csv_file, 'w', newline='') as cf:
                writer = csv.writer(cf)
                writer.writerow(["License Plate", "Model", "Manufacturer"])

                for detection in data:
                    writer.writerow([detection['license_plate'], detection['vehicle_data']['model'], detection['vehicle_data']['manufacturer']])

            print(f"Motorbike data successfully exported to {csv_file}")
        except Exception as e:
            print(f"Error exporting motorbike data: {e}")

        return csv_file

    def export_car_data_to_csv(self, json_file, csv_file):
        try:
            with open(json_file, 'r') as jf:
                data = json.load(jf)

            with open(csv_file, 'w', newline='') as cf:
                writer = csv.writer(cf)
                writer.writerow(["License Plate", "Model", "Manufacturer"])

                for detection in data:
                    writer.writerow([detection['license_plate'], detection['vehicle_data']['model'], detection['vehicle_data']['manufacturer']])

            print(f"Car data successfully exported to {csv_file}")
        except Exception as e:
            print(f"Error exporting car data: {e}")

        return csv_file
    
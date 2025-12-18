import json
import csv

class DetectionService:
    def __init__(self, detections_file: str):
        self.detections_file = detections_file

    def view_saved_detections(self):
        """
        Load and display saved detections from the JSON file.
        """
        try:
            with open(self.detections_file, 'r') as file:
                detections = json.load(file)

            for i, detection in enumerate(detections, start=1):
                print(f"Detection {i}:")
                print(f"  License Plate: {detection.get('license_plate', 'N/A')}")
                print(f"  Vehicle Data: {detection.get('vehicle_data', {})}")
                for car in detection['detected_cars']:
                    print(f"    - Box: {car['box']}, Confidence: {car['confidence']}")
            print("\n")
        except Exception as e:
            print(f"Error loading or displaying detections: {e}")

    def export_detections_to_csv(self, output_csv: str):
        """
        Export saved detections from JSON to CSV format.
        """
        try:
            with open(self.detections_file, 'r') as file:
                detections = json.load(file)

            with open(output_csv, 'w', newline='') as csvfile:
                fieldnames = ['License Plate', 'Vehicle Model', 'Vehicle Manufacturer', 'Car Bounding Box', 'Confidence']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for detection in detections:
                    for car in detection['detected_cars']:
                        writer.writerow({
                            'License Plate': detection.get('license_plate', 'N/A'),
                            'Vehicle Model': detection.get('vehicle_data', {}).get('model', 'Unknown'),
                            'Vehicle Manufacturer': detection.get('vehicle_data', {}).get('manufacturer', 'Unknown'),
                            'Car Bounding Box': car['box'],
                            'Confidence': car['confidence']
                        })

            print(f"Detections exported to {output_csv}")

        except Exception as e:
            print(f"Error exporting detections: {e}")

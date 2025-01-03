# services/food.py

import requests
from pyzbar.pyzbar import decode
import cv2

class FoodService:
    def __init__(self):
        self.base_url = "https://world.openfoodfacts.org/api/v0/product/"
        
    
    def get_nutrition_by_barcode(self, barcode):
        """Fetch nutrition details using a product barcode."""
        try:
            response = requests.get(f"{self.base_url}{barcode}.json")
            if response.status_code == 200:
                data = response.json()
                if "product" in data:
                    return self.parse_nutrition_data(data["product"])
                return {"error": "Product not found"}
            return {"error": f"API returned status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_nutrition_by_name(self, name):
        """Fetch nutrition details using a product name."""
        try:
            search_url = f"https://world.openfoodfacts.org/cgi/search.pl"
            params = {"search_terms": name, "search_simple": 1, "json": 1}
            response = requests.get(search_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if "products" in data and data["products"]:
                    return self.parse_nutrition_data(data["products"][0])
                return {"error": "No products found"}
            return {"error": f"API returned status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def parse_nutrition_data(self, product):
        """Extract key nutritional details."""
        try:
            nutrients = product.get("nutriments", {})
            return {
                "product_name": product.get("product_name", "Unknown"),
                "calories": nutrients.get("energy-kcal", "N/A"),
                "fat": nutrients.get("fat", "N/A"),
                "saturated_fat": nutrients.get("saturated-fat", "N/A"),
                "sugars": nutrients.get("sugars", "N/A"),
                "protein": nutrients.get("proteins", "N/A"),
                "salt": nutrients.get("salt", "N/A"),
            }
        except Exception as e:
            return {"error": str(e)}
def scan_barcode(self):
        """Scan a barcode using the webcam."""
        cap = cv2.VideoCapture(0)
        print("Point the camera at the barcode...")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame.")
                break

            barcodes = decode(frame)
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                print(f"Detected Barcode: {barcode_data}")
                cap.release()
                cv2.destroyAllWindows()
                return barcode_data

            cv2.imshow("Barcode Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return None

def calculate_macronutrient_percentage(self, nutrition_data):
        """Calculate macronutrient percentages."""
        try:
            total = (
                float(nutrition_data.get("calories", 0)) +
                float(nutrition_data.get("protein", 0)) +
                float(nutrition_data.get("fat", 0))
            )
            carbs = float(nutrition_data.get("carbohydrates", 0)) / total * 100
            protein = float(nutrition_data.get("protein", 0)) / total * 100
            fat = float(nutrition_data.get("fat", 0)) / total * 100
            return {
                "carbs_percentage": carbs,
                "protein_percentage": protein,
                "fat_percentage": fat,
            }
        except Exception as e:
            return {"error": f"Could not calculate macronutrient percentages: {e}"}

# services/food.py
import requests
import cv2
import json

class FoodService:
    def __init__(self, api_url="https://openfoodfacts-api.herokuapp.com/"):
        self.api_url = api_url

    def get_nutrition_by_barcode(self, barcode):
        """Fetch nutritional information using a barcode."""
        try:
            response = requests.get(f"{self.api_url}{barcode}.json")
            if response.status_code == 200:
                product_data = response.json()
                if 'product' in product_data:
                    product = product_data['product']
                    return {
                        "product_name": product.get("product_name", "Unknown"),
                        "calories": product.get("nutriments", {}).get("energy-kcal_100g", "N/A"),
                        "fat": product.get("nutriments", {}).get("fat_100g", "N/A"),
                        "saturated_fat": product.get("nutriments", {}).get("saturated-fat_100g", "N/A"),
                        "sugars": product.get("nutriments", {}).get("sugars_100g", "N/A"),
                        "protein": product.get("nutriments", {}).get("proteins_100g", "N/A"),
                        "salt": product.get("nutriments", {}).get("salt_100g", "N/A"),
                    }
                else:
                    return {"error": "Product not found."}
            else:
                return {"error": f"API Error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def calculate_macronutrient_percentage(self, nutrition_data):
        """Calculate macronutrient percentages (carbs, protein, fat)."""
        try:
            total_energy = (
                4 * float(nutrition_data.get("carbohydrates", 0)) +
                4 * float(nutrition_data.get("protein", 0)) +
                9 * float(nutrition_data.get("fat", 0))
            )
            if total_energy > 0:
                return {
                    "carbs_percentage": (4 * float(nutrition_data.get("carbohydrates", 0)) / total_energy) * 100,
                    "protein_percentage": (4 * float(nutrition_data.get("protein", 0)) / total_energy) * 100,
                    "fat_percentage": (9 * float(nutrition_data.get("fat", 0)) / total_energy) * 100,
                }
            else:
                return {"error": "Total energy is zero or unavailable."}
        except Exception as e:
            return {"error": str(e)}

    def scan_barcode(self):
        """Scan a barcode using the webcam."""
        try:
            cap = cv2.VideoCapture(0)
            barcode_detected = None
            detector = cv2.QRCodeDetector()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                decoded_text, points, _ = detector.detectAndDecode(frame)
                if decoded_text:
                    barcode_detected = decoded_text
                    break

                cv2.imshow("Barcode Scanner", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            return barcode_detected
        except Exception as e:
            return {"error": str(e)}

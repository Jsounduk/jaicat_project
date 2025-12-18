# services/health.py

import requests

class HealthService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.example.com/health"  # Replace with the actual API endpoint

    def get_nutrition_facts(self, food_item):
        """Fetch nutritional facts for a given food item."""
        url = f"{self.base_url}/nutrition?item={food_item}&apikey={self.api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()  # Assuming the API returns a JSON response
        else:
            return {"error": "Error fetching nutrition facts"}

    def is_healthy(self, food_item):
        """Determine if a food item is healthy based on its nutritional facts."""
        nutrition = self.get_nutrition_facts(food_item)

        if "error" in nutrition:
            return False

        # Example logic: check if calories are less than a threshold
        return nutrition.get("calories", 0) < 200  # Change the threshold as needed

    def get_recipes(self, ingredient):
        """Fetch recipes that include the specified ingredient."""
        url = f"{self.base_url}/recipes?ingredient={ingredient}&apikey={self.api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()  # Assuming the API returns a JSON response
        else:
            return {"error": "Error fetching recipes"}

# Example usage:
if __name__ == "__main__":
    health_service = HealthService(api_key="YOUR_API_KEY")
    
    # Get nutrition facts
    nutrition_info = health_service.get_nutrition_facts("apple")
    print("Nutrition Info:", nutrition_info)

    # Check if food item is healthy
    is_healthy = health_service.is_healthy("apple")
    print("Is Healthy:", is_healthy)

    # Get recipes
    recipes = health_service.get_recipes("chicken")
    print("Recipes:", recipes)

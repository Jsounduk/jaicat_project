import requests

class FitnessService:
    def __init__(self):
        self.api_key = "YOUR_API_KEY"  # Replace with your actual API key
        self.base_url = "https://api.fitness.com/v1/"  # Example API URL

    def get_workout_routines(self, goals):
        """Fetch workout routines based on fitness goals."""
        url = f"{self.base_url}workouts?goals={goals}&apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Error fetching workout routines."}

    def calculate_calories_burned(self, activity, duration):
        """Estimate calories burned for a specific activity."""
        url = f"{self.base_url}calories?activity={activity}&duration={duration}&apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('calories', "Unknown")
        else:
            return {"error": "Error fetching calories burned."}

    def get_fitness_tips(self):
        """Fetch general fitness tips."""
        url = f"{self.base_url}tips?apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Error fetching fitness tips."}

# Example usage
if __name__ == "__main__":
    fitness_service = FitnessService()
    print(fitness_service.get_workout_routines("weight_loss"))
    print(fitness_service.calculate_calories_burned("running", 30))
    print(fitness_service.get_fitness_tips())

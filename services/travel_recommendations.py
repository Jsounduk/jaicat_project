# services/travel_recommendations.py

class TravelRecommendations:
    def __init__(self):
        # Dictionary to hold travel destination categories and their suggestions
        self.destinations = {
            "beach": [
                "Hawaii",
                "Bahamas",
                "Maldives",
                "Seychelles",
                "Bora Bora"
            ],
            "mountain": [
                "Swiss Alps",
                "Rocky Mountains",
                "Himalayas",
                "Andes",
                "Appalachians"
            ],
            "city": [
                "New York City",
                "Paris",
                "Tokyo",
                "Barcelona",
                "London"
            ],
            "cultural": [
                "Rome",
                "Athens",
                "Jerusalem",
                "Beijing",
                "Istanbul"
            ],
            "adventure": [
                "Costa Rica",
                "New Zealand",
                "Iceland",
                "Patagonia",
                "South Africa"
            ]
        }

    def get_recommendations(self, category):
        """Return travel recommendations based on the category."""
        # Convert category to lower case to ensure case-insensitive matching
        category = category.lower()
        # Get recommendations from the dictionary
        recommendations = self.destinations.get(category, ["No recommendations available."])
        return recommendations

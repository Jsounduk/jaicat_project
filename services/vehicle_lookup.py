import requests

class VehicleLookupService:
    def __init__(self, api_key):
        self.api_key = api_key

    def lookup_vehicle(self, reg_plate):
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{reg_plate}?format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            vehicle_info = {
                "Make": data.get("Make"),
                "Model": data.get("Model"),
                "Year": data.get("ModelYear"),
                "Fuel": data.get("FuelTypePrimary")
            }
            return vehicle_info
        else:
            return "Vehicle not found or invalid registration."


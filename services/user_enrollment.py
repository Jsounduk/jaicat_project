import json
from cryptography.fernet import Fernet

class UserEnrollmentService:
    def __init__(self, encryption_key, user_data_path):
        self.encryption_key = encryption_key
        self.cipher = Fernet(self.encryption_key)
        self.user_data_path = user_data_path

    def save_user_data(self, user_data):
        """Save user data securely with encryption."""
        json_data = json.dumps(user_data).encode()
        encrypted_data = self.cipher.encrypt(json_data)
        with open(self.user_data_path, 'wb') as f:
            f.write(encrypted_data)

    def add_vehicle_to_user(self, user, vehicle_data):
        """Add a vehicle to the user's profile."""
        user['vehicles'].append(vehicle_data)
        self.save_user_data(user)
        return "Vehicle added to your profile."
    
    def add_motorbike_to_user(self, user, motorbike_data):
        """Add a motorbike to the user's profile."""
        user['motorbikes'].append(motorbike_data)
        self.save_user_data(user)
        return "Motorbike added to your profile."

    def add_car_to_user(self, user, car_data):
        """Add a car to the user's profile."""
        user['cars'].append(car_data)
        self.save_user_data(user)
        return "Car added to your profile."

# Example integration in main.py
from services.user_enrollment import UserEnrollmentService

class Jaicat:
    def __init__(self):
        # Initialize UserEnrollmentService
        self.user_enrollment_service = UserEnrollmentService(encryption_key='YOUR_ENCRYPTION_KEY', user_data_path='path/to/user_data.json')

    def add_vehicle(self, plate, model, make):
        """Add a vehicle to the current user's profile."""
        vehicle_data = {"plate": plate, "make": make, "model": model}
        response = self.user_enrollment_service.add_vehicle_to_user(self.current_user, vehicle_data)
        self.speak(response)
    
    def add_motorbike_to_user(self, user, motorbike_data):
        """Add a motorbike to the user's profile."""
        user['motorbikes'].append(motorbike_data)
        self.save_user_data(user)
        return "Motorbike added to your profile."

    def add_car_to_user(self, user, car_data):
        """Add a car to the user's profile."""
        user['cars'].append(car_data)
        self.save_user_data(user)
        return "Car added to your profile."

    def process_user_input(self, user_input):
        # Check if the user wants to add a vehicle
        if "add vehicle" in user_input.lower():
            plate = input("Enter the license plate: ")
            make = input("Enter the vehicle make: ")
            model = input("Enter the vehicle model: ")
            self.add_vehicle(plate, make, model)

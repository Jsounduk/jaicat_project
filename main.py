import csv
import pyttsx3
import speech_recognition as sr
import os
import json
import cv2
import face_recognition
import threading
import tensorflow as tf
import numpy as np
import webbrowser
import datetime
import random
import wikipedia
import smtplib
from email.message import EmailMessage
from tkinter import ttk
from tkinter import messagebox
import json
import vobject
import mysql.connector
from mysql.connector import Error
from SPARQLWrapper import SPARQLWrapper, JSON
import speech_recognition as sr
import pyttsx3
import tkinter as tk 
from jsgf import PublicRule, Literal, Grammar
from PIL import Image, ImageTk
import asyncio
from services.bluetooth_service import BluetoothService

from computer_vision.object_detection import ObjectDetection
from features.nlp import NLPSystem

from services.email_service import EmailService
from ui.JaicatUI import JaicatUI
from command.Commands import CommandProcessor

from services.weather_service import WeatherService
from services.calendar_service import CalendarService
from services.spotify_integration import SpotifyIntegration
from services.finance import FinanceService
from services.job_search import JobSearchService
from services.youtube_analysis import YouTubeAnalysis
from services.bluetooth_service import BluetoothService
from services.travel_recommendations import TravelRecommendations
from services.usb_cam import USBCam
from services.project_management import ProjectManagement
from services.phone_cam import PhoneCamera
from services.swann_cctv import SwannCCTV
from services.ip_cam import IPCamera
from services.food import FoodService
from services.file_analysis import FileAnalysisService
from services.business_management import BusinessManagementService
from services.phone_cam import PhoneCamera
from services.usb_cam import USBCam
from services.motorbike_parts import MotorbikePartsService
from services.detection_service import DetectionService
from utils.file_handling import read_file, write_to_file, file_exists, get_file_extension, list_files_in_directory
from network.socket_utils import create_socket, listen_for_connections, accept_connection, send_data, receive_data, close_socket
from machine_learning.tensorflow_utils import load_model, make_prediction, evaluate_model, preprocess_data
from lib.nlp.translation import TranslationService
from lib.nlp.spacy_utils import SpacyUtils
from lib.nlp.medical import MedicalNLP
from lib.nlp.fitness import FitnessNLP
from lib.nlp.engineering import EngineeringNLP
from lib.nlp.crime import CrimeAnalyzer
from lib.nlg.Social_media_post import SocialMediaPostGenerator
from cryptography.fernet import Fernet
from conversation.dialogue_manager import DialogueManager  # Import DialogueManager
from computer_vision.home_surveillance import HomeSurveillance
from computer_vision.contact_recognition import ContactRecognition
from computer_vision.car_model import UKCarModel
from computer_vision.license_plate_detection import LicensePlateDetection
from computer_vision.object_detection import ObjectDetection
from computer_vision.face_recognition import FaceRecognition
from computer_vision.motorbike_model import MotorbikeModel
from computer_vision.car_part_recognition import CarPartRecognition
from computer_vision.car_model import UKCarModel
from computer_vision.car_part_recognition import CarPartRecognition
from computer_vision.face_recognition import FaceRecognition
from computer_vision.license_plate_detection import LicensePlateDetection
from computer_vision.motorbike_model import MotorbikeModel
from computer_vision.car_model import UKCarModel
from computer_vision.visualization import DetectionViewer
from computer_vision.motorbike_model import MotorbikeModel







class Jaicat:
    def __init__(self):
        """Initialize Jaicat core logic."""
        print("Initializing Jaicat AI assistant...")

        # Initialize speech recognition engine
        self.r = sr.Recognizer()

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()

        # Initialize NLP engine
        self.nlp = NLPSystem()
        self.ui = JaicatUI(self)


        # Initialize services
        self.assistant = CommandProcessor(self)
        self.assistant.add_command("hello", lambda: print("Hello, how can I help you today?"))

        self.car_model_service = UKCarModel(
            "computer_vision/yolov7.weights", 
            "computer_vision/yolov7.cfg",      
            "computer_vision/coco.names",      
            "computer_vision/uk_plate_cascade.xml"
        )
        self.motorbike_model_service = MotorbikeModel(
            "computer_vision/yolov7.weights",  # Path to YOLOv7 weights
            "computer_vision/yolov7.cfg",      # Path to YOLOv7 config
            "computer_vision/coco.names",      # Path to COCO names
            "computer_vision/uk_plate_cascade.xml"  # Path to UK plate cascade
        )

        self.detection_service = DetectionService('computer_vision/detections.json')
        self.license_plate_detection = LicensePlateDetection()

        # Initialize the speech engine
        self.speech_engine = pyttsx3.init()
        self.speech_engine.setProperty('rate', 150)  # Set speech rate to 150


        # Initialize TTS
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)

        # Initialize Speech Recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Initialize the UI
        self.ui = JaicatUI(self)

        # Initialize services
        self.weather_service = WeatherService()
        self.calendar_service = CalendarService()
        self.finance_service = FinanceService()
        self.spotify_integration = SpotifyIntegration()
        self.youtube_analysis = YouTubeAnalysis()
        self.job_search_service = JobSearchService()
        self.travel_recommendations_service = TravelRecommendations()
        self.usb_cam_service = USBCam()
        self.project_management_service = ProjectManagement()
        self.phone_camera_service = PhoneCamera()
        self.swann_cctv_service = SwannCCTV(api_key='swann_api_key', base_url='swann_base_url')
        self.ip_camera_service = IPCamera(camera_url='camera_url')
        self.food_service = FoodService(api_key='food_api_key')
        self.file_analysis_service = FileAnalysisService()
        self.bluetooth_service = BluetoothService()
        self.business_management_service = BusinessManagementService()
        self.car_model_service = UKCarModel("computer_vision/yolov7.weights.pt", "computer_vision/yolov7.cfg", "computer_vision/coco.names.txt", "computer_vision/uk_plate_cascade.xml" )
        self.car_part_recognition_service = CarPartRecognition('computer_vision/yolov7.weights.pt', 'computer_vision/yolov7.cfg', 'computer_vision/coco.names.txt')
        self.enrollment_pictures_path = 'C:\\Users\\josh_\\Desktop\\jaicat_project\\enrollment_pictures\\'
        self.object_detection_service = ObjectDetection('computer_vision/yolov7.weights.pt', 'computer_vision/yolov7.cfg', 'computer_vision/coco.names.txt')
        self.car_model_service = UKCarModel("computer_vision/yolov7.weights.pt", "computer_vision/yolov7.cfg", "computer_vision/coco.names.txt")
        self.car_part_recognition_service = CarPartRecognition("computer_vision/yolov7.weights.pt", "computer_vision/yolov7.cfg", "computer_vision/coco.names.txt")
        self.object_detection_service = ObjectDetection("computer_vision/yolov7.weights.pt", "computer_vision/yolov7.cfg", "computer_vision/coco.names.txt")
        self.motorbike_model_service = MotorbikeModel("computer_vision/yolov7.weights.pt", "computer_vision/yolov7.cfg", "computer_vision/coco.names.txt")
        self.car_model_system = UKCarModel(weights_path="computer_vision/yolov7.weights.pt", cfg_path="computer_vision/yolov7.cfg", names_path="computer_vision/coco.names.txt")
        self.calendar_service = CalendarService()
        self.email_service = EmailService(encryption_key="your_generated_key_here")

        # Initialize Bluetooth service
        self.bluetooth_service = BluetoothService()

        # Initialize ML systems
        self.tensorflow_model = load_model('path/to/model.h5')


        # Initialize NLP systems
        self.nlp_system = NLPSystem()
        self.translation_service = TranslationService()
        self.spacy_utils = SpacyUtils()
        self.medical_nlp = MedicalNLP()
        self.fitness_nlp = FitnessNLP()
        self.engineering_nlp = EngineeringNLP()
        self.crime_analyzer = CrimeAnalyzer(data_path='path_to_your_crime_data.csv')
        self.social_media_post_generator = SocialMediaPostGenerator()

        # Initialize Computer Vision systems
        self.surveillance_system = HomeSurveillance()
        self.contact_recognition_system = ContactRecognition()
        self.car_model_system = UKCarModel(weights_path="computer_vision/yolov7.weights.pt", cfg_path="computer_vision/yolov7.cfg", names_path="computer_vision/coco.names.txt")

        # Initialize CommandProcessor
        self.command_processor = CommandProcessor(self)
        self.assistant.add_command("hello", lambda: print("Hello, how can I help you today?"))
        self.assistant.add_command("scan barcode", lambda: self.food_service.scan_barcode())
        self.assistant.add_command("analyze nutrients", lambda: self.process_food_query("analyze nutrients"))

        # Track current user and face recognition state
        self.current_user = None
        self.face_recognized = False
        self.enrollment_pictures_path = 'C:\\Users\\josh_\\Desktop\\jaicat_project\\enrollment_pictures\\'
        self.enrollment_json_path = 'C:\\Users\\josh_\\Desktop\\jaicat_project\\enrollment_json\\'


        # Encryption key for securing user data
        self.encryption_key = b'YOUR_ENCRYPTION_KEY_HERE'
        self.cipher = Fernet(self.encryption_key)
        
        # Initialize DialogueManager
        self.dialogue_manager = DialogueManager()
    def enroll_vehicle(self):
        """Allow the user to enroll a vehicle (car or motorbike)."""
        self.ui.speak("Please provide the vehicle type: car or motorbike.")
        with self.microphone as source:
            audio = self.recognizer.listen(source)
        try:
            vehicle_type = self.recognizer.recognize_google(audio).lower()
            if vehicle_type not in ["car", "motorbike"]:
                self.ui.speak("Invalid vehicle type. Please say either car or motorbike.")
                return

            self.ui.speak(f"Please provide the {vehicle_type} registration/license plate.")
            with self.microphone as source:
                audio = self.recognizer.listen(source)
            reg_plate = self.recognizer.recognize_google(audio)
            
            # Save the vehicle info to the user's encrypted data
            user_data = self.load_encrypted_data(f"{self.current_user}.json")
            if vehicle_type == "car":
                user_data['cars'] = user_data.get('cars', []) + [reg_plate]
            else:
                user_data['motorbikes'] = user_data.get('motorbikes', []) + [reg_plate]

            self.save_encrypted_data(user_data, f"{self.current_user}.json")
            self.ui.speak(f"{vehicle_type.capitalize()} with plate {reg_plate} added successfully.")
        
        except sr.UnknownValueError:
            self.ui.speak("Sorry, I couldn't understand that. Please try again.")
            self.enroll_vehicle()

    def recognize_vehicle_plate(self, detected_vehicle):
        """Match detected vehicle plates with user's enrolled vehicles."""
        # Assuming detected_vehicle is a dictionary with 'plate' and 'type'
        plate = detected_vehicle['plate']
        vehicle_type = detected_vehicle['type']

        user_data = self.load_encrypted_data(f"{self.current_user}.json")
        if vehicle_type == "car" and plate in user_data.get('cars', []):
            self.ui.speak(f"Car with registration {plate} belongs to you.")
        elif vehicle_type == "motorbike" and plate in user_data.get('motorbikes', []):
            self.ui.speak(f"Motorbike with registration {plate} belongs to you.")
        else:
            self.ui.speak(f"No match found for the {vehicle_type} with plate {plate}.")



    # Enrollment and User Management with Encryption
    def save_encrypted_data(self, data, file_path):
        """Save user data securely with encryption."""
        json_data = json.dumps(data).encode()
        encrypted_data = self.cipher.encrypt(json_data)
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)

    def load_encrypted_data(self, file_path):
        """Load user data securely by decrypting the file."""
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())

    def enroll_user(self):
        """Enroll the user by capturing their voice and name."""
        self.ui.speak("Please say your name after the tone.")
        with self.microphone as source:
            audio = self.recognizer.listen(source)
        try:
            name = self.recognizer.recognize_google(audio)
            self.ui.speak(f"Thank you {name}! Enrollment complete.")

            # Car and Motorbike Reg
            car_reg = input("Please provide your car's registration/license plate (or say 'none'):")
            motorbike_reg = input("Please provide your motorbike's registration/license plate (or say 'none'):")

            # Save user name
            self.known_face_names.append(name)

            # Record enrollment audio
            self.ui.speak("Please say your name after the tone.")
            with self.microphone as source:
                audio = self.recognizer.listen(source)
            with open(os.path.join(self.enrollment_pictures_path, f"{name}.wav"), 'wb') as f:
                f.write(audio.get_wav_data())

            # Record enrollment picture
            self.ui.speak("Please take a picture of yourself.")
            with self.microphone as source:
                audio = self.recognizer.listen(source)
            with open(os.path.join(self.enrollment_pictures_path, f"{name}.png"), 'wb') as f:
                f.write(audio.get_wav_data())
            
            # Save user data
            user_data = {
                "name": name,
                "admin_status": False,
                "accessible_features": ["nlp", "finance", "weather", "job_search"],
                "vehicles": {
                    "car_reg": car_reg if car_reg.lower() != "none" else None,
                    "motorbike_reg": motorbike_reg if motorbike_reg.lower() != "none" else None
                }
            }

            json_file_path = os.path.join(self.enrollment_json_path, f"{name}.json")
            self.save_encrypted_data(user_data, json_file_path)

            self.current_user = name
        except sr.UnknownValueError:
            self.ui.speak("Sorry, I didn't catch that. Please try again.")
            self.enroll_user()

    def recognize_face(self):
        self.ui.speak("Please take a picture of yourself.")
        temp_img = face_recognition.load_image_file('temp.png')
        face_encodings = face_recognition.face_encodings(temp_img)
        if not face_encodings:
            self.ui.speak("No face detected. Please try again.")
            return
        temp_face_encoding = face_encodings[0]

        self.known_faces, self.known_face_names = [], []
        for file in os.listdir(self.enrollment_pictures_path):
            if file.endswith(".png"):
                img = face_recognition.load_image_file(os.path.join(self.enrollment_pictures_path, file))
                face_encodings = face_recognition.face_encodings(img)
                if face_encodings:
                    self.known_faces.append(face_encodings[0])
                    self.known_face_names.append(file.split('.')[0])

        matches = face_recognition.compare_faces(self.known_faces, temp_face_encoding)
        if True in matches:
            first_match_index = matches.index(True)
            name = self.known_face_names[first_match_index]
            self.ui.speak(f"Welcome back, {name}.")
            self.load_user_data(name)

            user_data = self.load_encrypted_data(os.path.join(self.enrollment_json_path, f"{name}.json"))
            car_reg = user_data['vehicles']['car_reg']
            motorbike_reg = user_data['vehicles']['motorbike_reg']
            if car_reg:
                self.ui.speak(f"You have a car registered with the plate: {car_reg}.")
            if motorbike_reg:
                self.ui.speak(f"You have a motorbike registered with the plate: {motorbike_reg}.")
        else:
            self.ui.speak("Face not recognized. Please enroll.")
            self.enroll_user()

    def load_user_data(self, name):
        """Load user data for the recognized face."""
        json_file_path = os.path.join(self.enrollment_json_path, f"{name}.json")
        if os.path.exists(json_file_path):
            user_data = self.load_encrypted_data(json_file_path)
            self.ui.speak(f"Hello {user_data['name']}!")
            self.current_user = user_data['name']
        else:
            self.ui.speak("No user data found. Starting enrollment.")
            self.enroll_user()

    def process_user_input(self, user_input):
        """Send user input to DialogueManager to process."""
        response = self.dialogue_manager.process_user_input(user_input)
        self.ui.display_response(response)
        self.speak(response)

        if "detect motorbike" in user_input.lower():
            self.detect_and_fetch_motorbike_data()
        elif "identify motorbike part" in user_input.lower():
            part_images = ["path/to/front.png", "path/to/back.png"]  # Replace with actual image paths
            self.identify_motorbike_part(part_images)

    def detect_and_fetch_vehicle_data(self):
        """Use CarModel to detect car and fetch vehicle data."""
        print("Starting car detection...")
        self.car_model_service.start_detection()
        self.car_model_service.wait_for_detection()
        vehicle_data = self.car_model_service.get_vehicle_data()
        if vehicle_data:
            self.ui.speak(vehicle_data)
        else:
            self.ui.speak("No vehicle data found. Please try again.")
            self.car_model_service.stop_detection()
    def detect_and_fetch_motorbike_data(self):
        """Use MotorbikeModel to detect motorbike and fetch part data."""
        print("Starting motorbike detection...")
        self.motorbike_model_service.start_detection()

    def identify_motorbike_part(self, part_images):
        """Identify a motorbike part using MotorbikePartsService."""
        response = self.motorbike_parts_service.identify_part(part_images)
        self.speak(response)
    def add_motorbike(self, plate, model, make):
        """Add a motorbike to the current user's profile."""
        motorbike_data = {"plate": plate, "make": make, "model": model}
        response = self.user_enrollment_service.add_motorbike_to_user(self.current_user, motorbike_data)
        self.speak(response)

    def add_car(self, plate, model, make):
        """Add a car to the current user's profile."""
        car_data = {"plate": plate, "make": make, "model": model}
        response = self.user_enrollment_service.add_car_to_user(self.current_user, car_data)
        self.speak(response)
    
    def process_user_input(self, user_input):
        if "add motorbike" in user_input.lower():
            plate = input("Enter the license plate: ")
            make = input("Enter the motorbike make: ")
            model = input("Enter the motorbike model: ")
            self.add_motorbike(plate, make, model)
        elif "add car" in user_input.lower():
            plate = input("Enter the license plate: ")
            make = input("Enter the car make: ")
            model = input("Enter the car model: ")
            self.add_car(plate, make, model)
            
    def recognize_cars_in_camera(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detected_cars = self.car_model_service.detect_cars(frame)
            for (box, confidence) in detected_cars:
                x, y, w, h = box
                label = f"Car: {confidence:.2f}"
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow("Car Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


    def run(self):
        self.car_model_service.start_detection()

    def view_saved_detections(self):
        root = tk.Tk()
        detection_viewer = DetectionViewer(root)
        root.mainloop()

    def start_motorbike_surveillance(self):
        self.motorbike_model_service.start_detection()

    def process_user_input(self, user_input):
        intent, entities = self.nlp_system.process(user_input)
        if intent == "motorbike_surveillance":
            self.start_motorbike_surveillance()

    def play_song(self, song_title):
        # Add code to play the song here
        # For example, you can use the Spotify integration method
        self.display_response(f"Playing '{song_title}' via Spotify...")
        response = self.jaicat.spotify_integration.play_song(song_title)
        self.display_response(response)

    def display_calendar_events(self):
        events = self.calendar_service.get_upcoming_events()
        if events:
            event_text = "\n".join(events)
            self.display_response(f"Upcoming events:\n{event_text}")
        else:
            self.display_response("No upcoming events.")
    def control_bluetooth_device(self, device_name):
        response = self.bluetooth_service.connect_to_device(device_name)
        self.display_response(response)
def process_bluetooth_command(self, command):
    if "scan bluetooth" in command:
        devices = self.bluetooth_service.scan_devices()
    elif "connect to" in command:
        device_addr = command.split("connect to")[-1].strip()
        self.bluetooth_service.connect_device(device_addr)
    elif "disconnect" in command:
        self.bluetooth_service.disconnect_device()

def receive_data(self):
    """Receive data from the connected Bluetooth device."""
    if self.socket:
        try:
            data = self.socket.recv(1024)  # Adjust the buffer size as needed
            print(f"Received data: {data}")
            self.ui.speak(f"Received data: {data}")
        except Exception as e:
            self.ui.speak(f"Failed to receive data: {e}")
    else:
        self.ui.speak("No device connected.")


    def get_saved_detections(self):
        # Fetch saved detections from the detection service
        try:
            with open('computer_vision/detections.json', 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading detections: {e}")
            return []

    def export_detections_to_csv(self, detections):
        # Export saved detections to a CSV file
        try:
            with open('computer_vision/detections.csv', 'w') as file:
                writer = csv.writer(file)
                writer.writerow(["License Plate", "Model", "Manufacturer", "Date"])
                for detection in detections:
                    writer.writerow([detection['license_plate'], 
                                     detection['vehicle_data'].get('model', 'N/A'),
                                     detection['vehicle_data'].get('manufacturer', 'N/A'),
                                     detection.get('date', 'Unknown')])
            print("Detections exported successfully.")
        except Exception as e:
            print(f"Error exporting detections: {e}")

    def load_user_data(self, user_name):
        file_path = f"user_data/{user_name}.json"
        with open(file_path, "r") as file:
            user_data = json.load(file)
        return user_data

    def select_email_account(self, email_accounts):
        print("Available email accounts:")
        for idx, account in enumerate(email_accounts, start=1):
            print(f"{idx}- {account['address']}")
        self.ui.speak("Please select an email account by number.")
        selected_index = int(input("Enter number: ")) - 1  # Replace with GUI/voice input integration
        return selected_index

    def send_email(self, user_name, recipient_email, subject, message):
        user_data = self.load_user_data(user_name)
        email_accounts = user_data.get("email_accounts", [])
        if not email_accounts:
            self.ui.speak("No email accounts found.")
            return

        selected_index = self.select_email_account(email_accounts)
        selected_account = email_accounts[selected_index]
        decrypted_password = self.email_service.decrypt_password(selected_account["password"])

        response = self.email_service.send_email(
            smtp_server=selected_account["smtp_server"],
            smtp_port=selected_account["smtp_port"],
            sender_email=selected_account["address"],
            sender_password=decrypted_password,
            recipient_email=recipient_email,
            subject=subject,
            message=message
        )
        self.ui.speak(response)



    # Main Event Loop
    def run(self):
        """Start the Jaicat assistant."""
        print("Starting Jaicat...")
        self.ui.run()

class CalendarService:
    def get_current_date(self):
        return datetime.date.today()

if __name__ == "__main__":
    jaicat = Jaicat()
    jaicat.run()

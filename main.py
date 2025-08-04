import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import pyttsx3
import speech_recognition as sr
import random
import os
import json
import threading
import subprocess

from conversation.dialogue_manager import DialogueManager
from ui.JaicatUI import JaicatUI

# Services and integrations
from services.weather_service import WeatherService
from services.calendar_service import CalendarService
from services.spotify_integration import SpotifyIntegration
from services.detection_service import DetectionService
from services.finance import FinanceService
from services.job_search import JobSearchService
from services.youtube_analysis import YouTubeAnalysis
from services.travel_recommendations import TravelRecommendations
from services.usb_cam import USBCam
from services.project_management import ProjectManagement
from services.phone_cam import PhoneCamera
from services.swann_cctv import SwannCCTV
from services.ip_cam import IPCamera
from services.food import FoodService
from services.file_analysis import FileAnalysisService
from services.business_management import BusinessManagementService

class Jaicat:
    def __init__(self):
        print("Initializing the Jaicat AI assistant...")

        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 1.0)

        self.recognizer = sr.Recognizer()
        self.microphone = self.select_microphone()

        self.dialogue_manager = DialogueManager()

        self.current_user = None
        self.face_recognized = False
        self.current_mood = "neutral"
        self.ui = None

        self.load_services()

    def load_services(self):
        self.weather_service = WeatherService()
        self.calendar_service = CalendarService()
        self.spotify_integration = SpotifyIntegration()
      #  self.finance_service = FinanceService()
      #  self.job_search_service = JobSearchService()
      #  self.youtube_analysis = YouTubeAnalysis()
      #  self.travel_recommendations = TravelRecommendations()
      #  self.usb_cam_service = USBCam()
     #   self.project_management_service = ProjectManagement()
      #  self.phone_camera_service = PhoneCamera()
     #   self.swann_cctv_service = SwannCCTV()
       # self.ip_camera_service = IPCamera()
      #  self.food_service = FoodService()
     #   self.file_analysis_service = FileAnalysisService()
    #    self.business_management_service = BusinessManagementService()
        self.detection_service = DetectionService(detections_file="data/detections.json")

    def select_microphone(self):
        print("Available microphones:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  [{index}] {name}")
        return sr.Microphone(device_index=0)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def set_mood(self, mood):
        self.current_mood = mood
        if self.ui:
            self.ui.set_face(mood)

    def greet_user_on_boot(self):
        if not os.path.exists("user_data/enrollment.json"):
            self.set_mood("happy")
            self.speak("Hello there! I'm Jaicat. Let's get you enrolled.")
            self.display_response("Welcome to Jaicat! Please follow the instructions to enroll.")
            self.set_mood("neutral")
        else:
            with open("user_data/enrollment.json", "r") as f:
                user_data = json.load(f)
                preferred_names = user_data.get("preferred_names", ["boss"])
                greeting = random.choice(["Hello", "Hey", "Welcome back"])
                name = random.choice(preferred_names)
                self.set_mood("flirty")
                self.speak(f"{greeting}, {name}. I'm ready when you are 💋")

    def display_response(self, message):
        print("Status:", message)
        if self.ui:
            self.ui.display_response(message)
        else:
            print(message)

    def run(self):
        print("Jaicat core systems are running.")
        self.start_passive_listening()

    def start_passive_listening(self):
        self.listener_thread = threading.Thread(target=self.listen_for_wake_word)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def listen_for_wake_word(self):
        while True:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("👃 Listening for wake word...")
                try:
                    audio = self.recognizer.listen(source, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"🎤 Heard: {text}")
                    if any(alias in text.lower() for alias in ["jaicat", "jaycat", "jacat", "jay cat", "jai cat"]):
                        print("✅ Wake word triggered!")
                        self.speak("Yes babe, I’m listening 💋")
                        self.listen_for_command()
                except sr.UnknownValueError:
                    print("⚠️ Could not understand audio.")
                except sr.RequestError as e:
                    print(f"❌ Google API error: {e}")

    def listen_for_command(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("🎧 Listening for command...")
            try:
                audio = self.recognizer.listen(source, phrase_time_limit=6)
                command = self.recognizer.recognize_google(audio).lower()
                print(f"🎤 Command heard: {command}")
                self.process_user_input(command)
            except sr.UnknownValueError:
                self.speak("Sorry, I didn’t catch that. Try again, babe?")
                self.listen_for_command()
            except sr.RequestError as e:
                print(f"❌ Google API error during command: {e}")

    def process_user_input(self, user_input):
        try:
            response = self.dialogue_manager.process_user_input(user_input)
        except Exception as e:
            response = f"Oops! Something went wrong: {e}"
        if response == "shutdown_now":
            self.speak("Okay babe, shutting down. See you soon 💋")
            if self.ui:
                self.ui.window.destroy()
            os._exit(0)
        else:
            self.display_response(response)
            self.speak(response)

if __name__ == "__main__":
    print("Initializing the Jaicat AI assistant...")
    assistant = Jaicat()
    assistant.greet_user_on_boot()

    print("Assistant initialized. Connecting to UI...")
    ui = JaicatUI(assistant)
    assistant.ui = ui

    print("Launching Jaicat visual interface...")
    assistant_thread = threading.Thread(target=assistant.run)
    assistant_thread.daemon = True
    assistant_thread.start()

    ui.run()
    print("Jaicat has been closed. Exiting...")

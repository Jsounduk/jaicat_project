import cv2
import pygame
import numpy as np
import pyautogui
import oneDrive
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from .oneDrive import OneDriveClient
import pickle
import os.path
from datetime import datetime, timedelta
import requests
from outlook import Outlook


class JarvisVision:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)  # Use default camera (index 0)
        cv2.namedWindow("Jarvis Vision", cv2.WINDOW_NORMAL)
        self.one_drive_client = oneDrive.OneDriveClient()
        self.google_calendar_service = self.get_google_calendar_service()
        self.outlook_client = Outlook()

    def analyze_camera_feed(self):
        while True:
            # Capture a frame from the camera
            ret, frame = self.cap.read()

            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply thresholding to segment out objects of interest
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Find contours in the thresholded image
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Iterate through the contours and analyze them
            for contour in contours:
                # Calculate the area of the contour
                area = cv2.contourArea(contour)

                # Filter out small contours (e.g., noise)
                if area > 1000:
                    # Calculate the bounding rectangle of the contour
                    x, y, w, h = cv2.boundingRect(contour)

                    # Draw a rectangle around the object of interest
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Extract the ROI (Region of Interest) from the original frame
                    roi = frame[y:y + h, x:x + w]

                    # Analyze the ROI using OpenCV functions (e.g., face detection, object recognition)
                    # For demonstration purposes, we'll just display the ROI
                    cv2.imshow("ROI", roi)

            # Display the output
            cv2.imshow("Jarvis Vision", frame)

            # Exit on key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def analyze_image_file(self, image_path):
        # Load the image
        image = cv2.imread(image_path)

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to segment out objects of interest
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Iterate through the contours and analyze them
        for contour in contours:
            # Calculate the area of the contour
            area = cv2.contourArea(contour)

            # Filter out small contours (e.g., noise)
            if area > 1000:
                # Calculate the bounding rectangle of the contour
                x, y, w, h = cv2.boundingRect(contour)

                # Draw a rectangle around the object of interest
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Extract the ROI (Region of Interest) from the original image
                roi = image[y:y + h, x:x + w]

                # Analyze the ROI using OpenCV functions (e.g., face detection, object recognition)
                # For demonstration purposes, we'll just display the ROI
                cv2.imshow("ROI", roi)

        # Display the output
        cv2.imshow("Image Analysis", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def analyze_video_file(self, video_path):
        # Load the video
        cap = cv2.VideoCapture(video_path)

        while True:
            # Capture a frame from the video
            ret, frame = cap.read()

            if not ret:
                break

            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply thresholding to segment out objects of interest
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Find contours in the thresholded image
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Iterate through the contours and analyze them
            for contour in contours:
                # Calculate the area of the contour
                area = cv2.contourArea(contour)

                # Filter out small contours (e.g., noise)
                if area > 1000:
                    # Calculate the bounding rectangle of the contour
                    x, y, w, h = cv2.boundingRect(contour)

                    # Draw a rectangle around the object of interest
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Extract the ROI (Region of Interest) from the original frame
                    roi = frame[y:y + h, x:x + w]

                    # Analyze the ROI using OpenCV functions (e.g., face detection, object recognition)
                    # For demonstration purposes, we'll just display the ROI
                    cv2.imshow("ROI", roi)

            # Display the output
            cv2.imshow("Video Analysis", frame)

            # Exit on key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def analyze_one_drive_images(self):
        # Get the list of images in OneDrive
        images = self.one_drive_client.get_images()

        # Iterate through the images and analyze them
        for image in images:
            # Download the image
            image_path = self.one_drive_client.download_image(image['id'])

            # Analyze the image
            self.analyze_image_file(image_path)

    def integrate_project_management_and_calendar_apis(self):
        # Integrate project management and calendar APIs to manage tasks and events.
        pass

    def integrate_google_calendar_api(self):
        # Integrate Google Calendar API to manage tasks and events.
        pass

    def integrate_outlook_api(self):
        # Integrate Outlook API to manage tasks and events.
        pass

    def get_google_calendar_service(self):
        # Google Calendar API credentials
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        CLIENT_SECRET_FILE = 'credentials.json'
        APPLICATION_NAME = 'Jarvis Vision'

        # Load the credentials
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # Build the Google Calendar service
        service = build('calendar', 'v3', credentials=creds)

        return service

    def run(self):
        self.analyze_camera_feed()
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    jarvis_vision = JarvisVision()
    jarvis_vision.run()

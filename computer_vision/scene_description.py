# computer_vision/scene_description.py

import cv2
from computer_vision.object_detection import detect_objects
from utils.speech import Speech

speech = Speech()

def describe_scene_from_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speech.speak("Sorry, I can't access the camera.")
        return

    speech.speak("Looking now...")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        speech.speak("Something went wrong with the camera.")
        return

    labels = detect_objects(frame)
    if not labels:
        speech.speak("I don't see anything interesting.")
        return

    description = f"I see: {', '.join(labels)}"
    print("[vision] Scene:", description)
    speech.speak(description)
    return description

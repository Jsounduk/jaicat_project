# C:\Users\josh_\Desktop\jaicat_project\image_processing.py

import cv2

def capture_frame():
    # Capture a single frame from the webcam
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()
    video_capture.release()
    return frame

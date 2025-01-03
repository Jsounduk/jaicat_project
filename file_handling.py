# C:\Users\josh_\Desktop\jaicat_project\file_handling.py

import cv2

def save_image_file(image, file_name):
    cv2.imwrite(file_name, image)

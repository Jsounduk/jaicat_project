import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        pass

    def load_image(self, image_path):
        """
        Load an image from a file path
        """
        return cv2.imread(image_path)

    def resize_image(self, image, width, height):
        """
        Resize an image to a specified width and height
        """
        return cv2.resize(image, (width, height))

    def convert_to_grayscale(self, image):
        """
        Convert an image to grayscale
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def apply_threshold(self, image, threshold_value):
        """
        Apply a threshold to an image
        """
        _, thresh = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
        return thresh

    def detect_faces(self, image):
        """
        Detect faces in an image using OpenCV's Haar cascade classifier
        """
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = self.convert_to_grayscale(image)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces

    def draw_rectangles(self, image, rectangles):
        """
        Draw rectangles on an image
        """
        for (x, y, w, h) in rectangles:
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        return image

    def save_image(self, image, image_path):
        """
        Save an image to a file path
        """
        cv2.imwrite(image_path, image)

# Example usage:
if __name__ == "__main__":
    image_processor = ImageProcessor()
    image = image_processor.load_image("image.jpg")
    resized_image = image_processor.resize_image(image, 640, 480)
    grayscale_image = image_processor.convert_to_grayscale(resized_image)
    thresholded_image = image_processor.apply_threshold(grayscale_image, 127)
    faces = image_processor.detect_faces(resized_image)
    drawn_image = image_processor.draw_rectangles(resized_image, faces)
    image_processor.save_image(drawn_image, "output.jpg")
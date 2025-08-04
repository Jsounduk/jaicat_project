import cv2
import face_recognition
import os

class FaceRecognition:
    def __init__(self, enrollment_pictures_path):
        self.enrollment_pictures_path = enrollment_pictures_path
        self.known_face_encodings = []
        self.known_face_names = []

        self.load_known_faces()

    def load_known_faces(self):
        for image_file in os.listdir(self.enrollment_pictures_path):
            if image_file.endswith('.png'):
                image = face_recognition.load_image_file(os.path.join(self.enrollment_pictures_path, image_file))
                encoding = face_recognition.face_encodings(image)[0]
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(os.path.splitext(image_file)[0])

    def recognize_faces(self, frame):
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        face_names = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]

            face_names.append(name)

        return face_locations, face_names

# computer_vision/contact_recognition.py

import cv2
import face_recognition
import os

class ContactRecognition:
    def __init__(self, enrollment_folder='enrollment_pictures'):
        self.enrollment_folder = enrollment_folder
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_enrolled_faces()

    def load_enrolled_faces(self):
        """Load enrolled faces from the specified directory."""
        print("Loading enrolled faces...")
        for image_file in os.listdir(self.enrollment_folder):
            if image_file.endswith(".png") or image_file.endswith(".jpg"):
                image_path = os.path.join(self.enrollment_folder, image_file)
                image = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(image)[0]
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(os.path.splitext(image_file)[0])  # Use filename without extension as name

    def recognize_faces(self, frame):
        """Recognize faces in the given frame."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        recognized_names = []
        for encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, encoding)
            name = "Unknown"

            # Check if a match was found
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]

            recognized_names.append(name)

        return face_locations, recognized_names

    def start_recognition(self):
        """Start the face recognition process."""
        print("Starting contact recognition...")
        video_capture = cv2.VideoCapture(0)

        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Unable to capture video.")
                break

            face_locations, recognized_names = self.recognize_faces(frame)

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, recognized_names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow('Contact Recognition', frame)

            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    contact_recognition = ContactRecognition()
    contact_recognition.start_recognition()

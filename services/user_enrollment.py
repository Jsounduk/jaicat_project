from computer_vision.face_recognition import FaceRecognition
import cv2
import face_recognition
import os

class UserEnrollmentService:
    def __init__(self):
        self.face_system = FaceRecognition()

    def start_enrollment(self, name):
        print(f"[enroll] Enrolling new user: {name}")
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            cv2.imshow("Enrollment", frame)
            if cv2.waitKey(1) & 0xFF == ord("s"):
                success = self.face_system.add_new_user(name, frame)
                break

        cap.release()
        cv2.destroyAllWindows()
        return success
    
    def enroll_face(name: str):
        cam = cv2.VideoCapture(0)
        print(f"[enrollment] Capturing face for: {name}")

        while True:
            ret, frame = cam.read()
            cv2.imshow("Enrollment", frame)
            if cv2.waitKey(1) & 0xFF == ord('c'):
                path = f"enrollment_pictures/{name}.png"
                cv2.imwrite(path, frame)
                break

        cam.release()
        cv2.destroyAllWindows()
        print("[enrollment] Face captured.")

        img = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(img)[0]
    


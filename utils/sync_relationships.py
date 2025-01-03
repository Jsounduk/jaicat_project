import cv2
import face_recognition
from sklearn.neighbors import NearestNeighbors

# Load the facial recognition model
face_recognition_model = face_recognition.FaceRecognition()

# Load the phone contacts and photos
contacts = []  # list of contacts with names and relationships
photos = []  # list of photos with faces and labels

# Iterate through the contacts and photos
for contact in contacts:
    name = contact["name"]
    relationship = contact["relationship"]
    photo = contact["photo"]
    
    # Extract the face from the photo
    face = face_recognition_model.extract_face(photo)
    
    # Add the face to the library
    face_recognition_model.add_face(face, name, relationship)

# Create a nearest neighbors model to recognize faces
nn_model = NearestNeighbors(n_neighbors=1, algorithm="ball_tree")
nn_model.fit(face_recognition_model.faces)

# Define a function to recognize people in new photos
def recognize_people(photo):
    face = face_recognition_model.extract_face(photo)
    distances, indices = nn_model.kneighbors([face])
    name = face_recognition_model.names[indices[0][0]]
    relationship = face_recognition_model.relationships[indices[0][0]]
    return name, relationship

# Example usage:
photo = cv2.imread("new_photo.jpg")
name, relationship = recognize_people(photo)
print(f"Recognized person: {name} ({relationship})")
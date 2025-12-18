import face_recognition
from PIL import Image
from googleapiclient.discovery import build
from onedrive import OneDrive

# Set up Google Contacts API
contacts_service = build('people', 'v1')

# Set up OneDrive API
onedrive = OneDrive()

# Load the user's contacts
contacts = contacts_service.people().list().execute()

# Create a dictionary to store the user's contacts and their corresponding images
contact_images = {}

# Loop through the user's contacts and download their profile pictures
for contact in contacts['connections']:
    contact_id = contact['resourceName']
    contact_name = contact['names'][0]['displayName']
    contact_image_url = contact['photos'][0]['url']
    contact_image = onedrive.get_file(contact_image_url)
    contact_images[contact_name] = contact_image

# Load the user's images from OneDrive
images = onedrive.get_files()

# Loop through the user's images and recognize the faces
for image in images:
    image_path = image['path']
    image_data = onedrive.get_file(image_path)
    image = face_recognition.load_image_file(image_data)
    faces = face_recognition.face_locations(image)
    for face in faces:
        face_encoding = face_recognition.face_encodings(image, known_face_locations=[face])[0]
        # Compare the face encoding to the user's contacts
        for contact_name, contact_image in contact_images.items():
            contact_face_encoding = face_recognition.face_encodings(contact_image)[0]
            if face_recognition.compare_faces([contact_face_encoding], face_encoding):
                print(f"Found {contact_name} in image {image_path}")

# Allow the user to hash tag images with contact names
def hash_tag_image(image_path, contact_name):
    # Get the contact's image
    contact_image = contact_images[contact_name]
    # Get the image data
    image_data = onedrive.get_file(image_path)
    # Load the image
    image = face_recognition.load_image_file(image_data)
    # Recognize the faces in the image
    faces = face_recognition.face_locations(image)
    for face in faces:
        face_encoding = face_recognition.face_encodings(image, known_face_locations=[face])[0]
        # Compare the face encoding to the contact's face encoding
        if face_recognition.compare_faces([contact_image], face_encoding):
            print(f"Found {contact_name} in image {image_path}")
            # Link the image to the contact
            contact_images[contact_name].append(image_path)

# Test the function
hash_tag_image("image1.jpg", "John Doe")

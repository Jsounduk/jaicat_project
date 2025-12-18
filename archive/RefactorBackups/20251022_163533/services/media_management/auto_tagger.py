# services/media_management/auto_tagger.py

from computer_vision.face_recognition import recognize_faces
from computer_vision.object_detection import detect_objects
from security.encryption_utils import save_encrypted_json

def auto_tag_image(image_path):
    from PIL import Image
    img = Image.open(image_path).convert("RGB")

    # Step 1: Detect faces
    faces = recognize_faces(img)  # returns ["Jay", "Samantha"]

    # Step 2: Detect objects
    objects = detect_objects(img)  # returns ["motorbike", "helmet"]

    # Combine tags
    tags = list(set(faces + objects))

    # Save encrypted tag metadata
    metadata = {
        "image": image_path,
        "tags": tags
    }
    save_encrypted_json(image_path + ".json", metadata)

    return tags


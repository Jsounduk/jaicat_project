# core/assets.py
from PIL import Image

class Assets:
    def face_for_mood(self, mood: str) -> Image.Image:
        mapping = {
            "happy": "face_happy.png",
            "flirty": "face_flirty.png",
            "sad": "face_sad.png",
            "neutral": "face_neutral.png",
        }
        path = mapping.get(mood, mapping["neutral"])
        return Image.open(path)

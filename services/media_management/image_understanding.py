# services/media_management/image_understanding.py

from typing import Dict, Any, List

from services.media_management.tag_ai import generate_tags
from services.media_management.body_part_detector import detect_body_parts
from services.media_management.clothing_and_pose_detector import detect_clothing_and_pose
from services.media_management.yolo_pose import run_yolo_pose
from services.media_management.face_loader import load_known_faces
from computer_vision.face_recognition import recognize_faces

class ImageUnderstandingService:
    def __init__(self, faces_dir="services/media_management/faces"):
        # preload face DB for speed
        self.known_encodings, self.known_names = load_known_faces(faces_dir)

    def analyse(self, image_path: str) -> Dict[str, Any]:
        """
        Run your existing vision stack and return a structured dict
        the NLG/LLM can talk about.
        """
        data: Dict[str, Any] = {"image": image_path}

        # 1) BLIP/CLIP tags
        auto_tags: List[str] = generate_tags(image_path)
        data["raw_tags"] = auto_tags

        # 2) Clothing / pose / body parts
        fashion_tags, _ = detect_clothing_and_pose(image_path)
        pose_tags, _ = run_yolo_pose(image_path)
        body_tags, _ = detect_body_parts(image_path)

        extra = set((fashion_tags or []) + (pose_tags or []) + (body_tags or []))
        data["vision_tags"] = sorted(extra)

        # 3) Faces
        # recognize_faces() already exists and is used in auto_tagger
        faces = recognize_faces(image_path, self.known_encodings, self.known_names)
        data["faces"] = faces or []

        # 4) Unified tag list
        all_tags = set(auto_tags)
        all_tags.update(extra)
        all_tags.update(faces or [])
        data["all_tags"] = sorted(all_tags)

        return data

    def to_caption_prompt(self, analysis: Dict[str, Any]) -> str:
        """
        Turn the analysis dict into a text prompt that your NLG/LLM
        can turn into a nice description.
        """
        tags = ", ".join(analysis.get("all_tags", [])) or "no tags"
        faces = ", ".join(analysis.get("faces", [])) or "no recognised faces"

        return (
            f"Image analysis:\n"
            f"- Tags: {tags}\n"
            f"- Recognised people: {faces}\n"
            f"Write 1–3 natural sentences describing this image."
        )
# services/media_management/image_understanding.py (bottom)

from conversation.nlg import ContextualResponder

_responder = None

def describe_image_with_llm(image_path: str) -> str:
    global _responder
    if _responder is None:
        _responder = ContextualResponder()

    service = ImageUnderstandingService()
    analysis = service.analyse(image_path)
    prompt = service.to_caption_prompt(analysis)
    return _responder.respond(prompt)

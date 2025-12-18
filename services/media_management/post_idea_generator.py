# services/media_management/post_idea_generator.py

from lib.nlg.Social_media_post import generate_caption
from services.media_management.auto_tagger import auto_tag_image

def create_post_idea(image_path, mood="flirty"):
    tags = auto_tag_image(image_path)
    caption = generate_caption(tags, mood)
    return {
        "image": image_path,
        "caption": caption,
        "tags": tags
    }

# conversation/nlu.py

import re
from dateparser import parse

class NLU:
    def extract_intent_and_entities(self, text):
        text = text.lower().strip()

        # --- image intents ---
        if "describe this" in text or "what's in this" in text or "whats in this" in text:
            return "describe_current_image", {}
        if "describe image" in text or "describe the picture" in text:
            return "describe_current_image", {}
        if text.startswith("find images of ") or text.startswith("find pictures of "):
            subject = text.replace("find images of", "").replace("find pictures of", "").strip()
            return "search_images_by_tag", {"tag": subject}

        # existing intents…
        if "weather" in text:
            return "get_weather", {}
        elif "play music" in text:
            return "play_music", {}
        elif "calendar" in text:
            return "get_calendar", {}
        elif "capital of" in text:
            match = re.search(r"capital of (\w+)", text)
            if match:
                return "get_capital", {"country": match.group(1)}

        return "unknown", {}

    def extract_datetime(text):
        dt = parse(text)
        return dt if dt else None

# services/media_management/feedback_logger.py

import os
import json

FEEDBACK_LOG_PATH = "services/media_management/tag_feedback_log.json"

def log_feedback(image_path, auto_tags, chosen_tags, correction_type="image"):
    """
    Log manual corrections or teaching events.
    :param image_path: str - image being tagged
    :param auto_tags: list[str] - tags auto-suggested by Jaicat
    :param chosen_tags: list[str] - tags actually chosen by user
    :param correction_type: "image" or "region"
    """
    os.makedirs(os.path.dirname(FEEDBACK_LOG_PATH), exist_ok=True)
    entry = {
        "image": image_path,
        "auto_tags": auto_tags,
        "chosen_tags": chosen_tags,
        "correction_type": correction_type
    }
    try:
        if os.path.exists(FEEDBACK_LOG_PATH):
            with open(FEEDBACK_LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
        data.append(entry)
        with open(FEEDBACK_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to log feedback: {e}")

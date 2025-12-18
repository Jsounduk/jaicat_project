# conversation/dialogue_manager.py
from __future__ import annotations

import traceback
from typing import Optional, Tuple, Any, Dict

# NLU can vary across branches; handle both common APIs.
try:
    from conversation.nlu import NLU
except Exception:
    NLU = None  # we'll guard calls below

# Your nlg.py exposes ContextualResponder (not NLG)
try:
    from conversation.nlg import ContextualResponder as NLG
except Exception:
    NLG = None

# Optional vision / media imports
try:
    from services.media_management.image_understanding import (
        describe_image_with_llm,
    )
except Exception:
    describe_image_with_llm = None

try:
    from services.media_management.media_search import find_by_tag
except Exception:
    find_by_tag = None

# Shared app context (for current image, active user, etc.)
try:
    from app import context as app_context
except Exception:
    app_context = None


class DialogueManager:
    """
    Orchestrates open-ended chat:
      - asks NLU for (intent, entities) if available
      - handles some light intents directly (greetings, image commands, etc.)
      - if no command intent, asks NLG/LLM to generate a reply
      - graceful fallbacks if parts are missing
    """

    def __init__(self):
        self.nlu = NLU() if NLU else None
        self.nlg = NLG() if NLG else None

    # ---------- Public API ----------

    def process_user_input(self, text: str, user: str = "Jay"):
        """
        Main entry: text -> (intent, entities) -> response string.
        """
        try:
            intent, entities = self._safe_nlu(text)

            # ----- small-talk intents -----
            if intent in {"greet", "hello", "hi"}:
                return f"Hey {user}. What do you need?"
            if intent in {"goodbye", "bye"}:
                return "Catch you later."
            if intent in {"thanks", "thank_you"}:
                return "You’re welcome."

            # ----- image / media intents -----

            # Describe currently open image (e.g. "Jaicat, describe this picture")
            if intent == "describe_current_image":
                image_path = self._get_current_image_path()
                if not image_path:
                    return "I don’t have an image open to look at right now."
                if not describe_image_with_llm:
                    return "I’m not wired up for image descriptions in this build."
                try:
                    return describe_image_with_llm(image_path)
                except Exception:
                    traceback.print_exc()
                    return "I hit a snag trying to describe that image."

            # Tag-based search (e.g. "find images of phoenix tattoos")
            if intent == "search_images_by_tag":
                tag = None
                if isinstance(entities, dict):
                    tag = entities.get("tag")
                elif isinstance(entities, (list, tuple)) and entities:
                    # allow shapes like [{'tag': 'phoenix'}] or ["phoenix"]
                    first = entities[0]
                    if isinstance(first, dict):
                        tag = first.get("tag")
                    else:
                        tag = str(first)

                if not tag:
                    return "Tell me what you want me to look for, like 'find images of phoenix tattoos'."

                if not find_by_tag:
                    return "Image search isn’t connected in this build."

                try:
                    matches = find_by_tag(tag)
                except Exception:
                    traceback.print_exc()
                    return "Something went wrong while searching your images."

                if not matches:
                    return f"I couldn’t find anything tagged with '{tag}'."
                # UI layer can decide how to display these; we just report.
                return f"I found {len(matches)} images tagged with '{tag}'."

            # ----- fallback to free-form chat -----
            return self._freeform(text)

        except Exception as e:
            print("[DialogueManager] Error:", e)
            traceback.print_exc()
            return "I hit a snag thinking about that."

    # ---------- Helpers ----------

    def _safe_nlu(self, text: str) -> Tuple[Optional[str], Any]:
        """
        Return (intent, entities) from whatever NLU shape you have.

        Supports:
          - (intent, entities)
          - {'intent': 'x', 'entities': [...]}
          - {'intent': 'x', 'entities': {...}}
        """
        if not self.nlu:
            return None, []

        try:
            parsed = None
            # prefer extract_intent_and_entities
            if hasattr(self.nlu, "extract_intent_and_entities"):
                parsed = self.nlu.extract_intent_and_entities(text)
            elif hasattr(self.nlu, "extract"):
                parsed = self.nlu.extract(text)
        except Exception:
            return None, []

        if isinstance(parsed, dict):
            return parsed.get("intent"), parsed.get("entities") or []
        if isinstance(parsed, (list, tuple)) and parsed:
            intent = parsed[0]
            entities = parsed[1] if len(parsed) > 1 else []
            return intent, entities

        return None, []

    def _freeform(self, text: str) -> str:
        """
        Ask your NLG/LLM. Your ContextualResponder already has respond().
        If you later wire real LLM generation, implement generate_text(text).
        """
        if self.nlg:
            # Prefer respond() if available
            if hasattr(self.nlg, "respond"):
                try:
                    return str(self.nlg.respond(text))
                except Exception:
                    traceback.print_exc()
            # Fallback to generate_text(text)
            if hasattr(self.nlg, "generate_text"):
                try:
                    return str(self.nlg.generate_text(text))
                except Exception:
                    traceback.print_exc()

        # last resort echo (so the UI always shows *something*)
        return f"You said: {text}"

    def _get_current_image_path(self) -> Optional[str]:
        """
        Fetch the 'current image' from shared app context (set by the sorter UI).
        """
        if app_context and hasattr(app_context, "current_image_path"):
            return getattr(app_context, "current_image_path")
        return None

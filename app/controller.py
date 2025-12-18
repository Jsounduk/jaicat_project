# app/controller.py
from __future__ import annotations
from typing import Any, Dict, Optional
import threading

try:
    import speech_recognition as sr  # optional (for start_listening)
    _HAS_SR = True
except Exception:
    _HAS_SR = False


class Controller:
    """
    Thin orchestration between UI and conversation/services.

    Responsibilities:
      - run text turns (text -> NLU -> command/router or DM/RAG -> NLG)
      - adapt mood/voice from NLP sentiment
      - speak via injected TTS; mirror to UI if present
      - optionally listen on mic (guarded) and handle wake hooks
    """

    def __init__(self, services, router):
        # DI container + command router
        self.services = services
        self.router = router

        # Core brains
        self.nlp = services.resolve("nlp")
        self.nlu = services.resolve("nlu")
        self.nlg = services.resolve("nlg")
        self.dm = services.resolve("dialogue_manager")

        # Integrations (optional)
        self.spotify = services.try_resolve("spotify")
        self.weather = services.try_resolve("weather")
        self.calendar = services.try_resolve("calendar")

        # Speech / TTS
        self.speech = services.try_resolve("speech")
                # Startup hello (best-effort)
        if self.speech:
            try:
                self.speak("Hello, I am Jaicat. Ready when you are.")
            except Exception:
                pass
        self.wake = services.try_resolve("wake_word")
        if self.wake:
            try:
                self.wake.start(self.on_wake)
            except Exception:
                pass


        # Runtime state
        self.ui: Optional[Any] = None
        self.active_user: str = "Jay"
        self.tenant: str = "public"
        self.mood: str = "neutral"

    # ---------- UI & Wake ----------

    def set_ui(self, ui: Any) -> None:
        self.ui = ui
        # Propagate tenant into DM context if it exists
        if hasattr(self.dm, "context") and isinstance(self.dm.context, dict):
            self.dm.context["tenant"] = self.tenant

    def on_wake(self) -> None:
        self._bring_ui_foreground()
        self._set_mood("attentive")
        self.speak("Yes, boss?")
        # Listen once for the actual command after the wake word
        self.start_listening(timeout=30.0)

    # ---------- Main turn ----------

    def process_user_text(self, text: str) -> str:
        """
        Full text pipeline: NLU → Commands/DM → NLG → TTS/UI.
        Returns the final text response (for logs/tests).
        """
        # 1) sentiment → mood/voice
        sentiment = self._safe_sentiment(text)
        self._apply_sentiment(sentiment)

        # 2) NLU parse (tolerant to different return shapes)
        intent, entities = self._safe_nlu(text)

        # 3) Command path?
        if not intent:
            # keyword fallback for UI button strings
            low = (text or "").strip().lower()
            if "weather" in low:
                intent = "request_weather"
            elif "list events" in low or "calendar" in low:
                intent = "list_events"
            elif "play music" in low or low.startswith("play "):
                intent = "play_music"
            elif "start surveillance" in low or "surveillance" in low:
                intent = "start_surveillance"

        if intent and self.router.can_handle(intent):
            result = self.router.handle(intent, entities=entities, text=text, ctx=self)
            self.speak(result)
            return result



        # 4) Dialogue path (RAG/LLM via DialogueManager)
        if hasattr(self.dm, "process_user_input"):
            ans = self.dm.process_user_input(text, user=self.tenant)
            # Support (answer, sources) tuple
            if isinstance(ans, tuple):
                answer, sources = ans
                self.speak(answer)
                if sources:
                    refs = "; ".join(
                        f"{(h or {}).get('source','?')}→{(h or {}).get('uri','')}"
                        if isinstance(h, dict) else str(h)
                        for h in (sources or [])
                    )
                    return f"{answer}\n\nSources: {refs}"
                return answer
            self.speak(str(ans))
            return str(ans)

        # 5) Fallback NLG only
        reply = self._safe_nlg(text)
        self.speak(reply)
        return reply

    # ---------- Speech / Mic ----------

    def start_listening(self, timeout: float = 5.0) -> None:
        """
        Optional SR loop for quick tests. Safe if speech_recognition is missing.
        """
        if not _HAS_SR:
            self.speak("Mic not available on this build.")
            return

        def listen_loop():
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                try:
                    audio = r.listen(source, timeout=timeout)
                    utterance = r.recognize_google(audio)
                    self.process_user_text(utterance)
                except Exception:
                    self.speak("Sorry, I didn’t catch that.")

        threading.Thread(target=listen_loop, daemon=True).start()

    # ---------- Helpers ----------

    def speak(self, text: str) -> None:
        """
        Send speech out via TTS; mirror on UI if present.
        """
        if self.speech and hasattr(self.speech, "speak"):
            # Try mood-aware voice
            if hasattr(self.speech, "set_voice_by_sentiment"):
                self.speech.set_voice_by_sentiment(self._sentiment_alias(self.mood))
            self.speech.speak(text)
        if self.ui and hasattr(self.ui, "speak"):
            self.ui.speak(text)

    def _safe_sentiment(self, text: str) -> str:
        try:
            return str(self.nlp.analyze_sentiment(text))
        except Exception:
            return "neutral"

    def _apply_sentiment(self, sentiment: str) -> None:
        # map sentiment → mood
        mood = {
            "positive": "happy",
            "negative": "sad",
            "neutral": "neutral"
        }.get(sentiment, "neutral")
        self._set_mood(mood)

    def _set_mood(self, mood: str) -> None:
        self.mood = mood
        if self.ui and hasattr(self.ui, "set_face_by_mood"):
            self.ui.set_face_by_mood(mood)
        elif self.ui and hasattr(self.ui, "set_mood"):
            self.ui.set_mood(mood)

    def _sentiment_alias(self, mood: str) -> str:
        # convert UI mood back to sentiment-ish label for TTS voice switch
        return {
            "happy": "positive",
            "sad": "negative",
            "neutral": "neutral",
            "attentive": "neutral",
        }.get(mood, "neutral")

    def _safe_nlu(self, text: str) -> tuple[Optional[str], list]:
        """
        Allow both shapes:
          - (intent, entities)
          - {'intent': 'x', 'entities': [...]}
        """
        try:
            parsed = self.nlu.extract_intent_and_entities(text)
        except AttributeError:
            parsed = self.nlu.extract(text)  # alternate method name
        except Exception:
            return None, []

        if isinstance(parsed, dict):
            return parsed.get("intent"), parsed.get("entities") or []
        if isinstance(parsed, (list, tuple)) and len(parsed) >= 1:
            intent = parsed[0]
            entities = parsed[1] if len(parsed) > 1 else []
            return intent, entities
        return None, []

    def _safe_nlg(self, text: str) -> str:
        try:
            if hasattr(self.nlg, "respond"):
                return str(self.nlg.respond(text))
            if hasattr(self.nlg, "generate_text"):
                return str(self.nlg.generate_text(text))
        except Exception:
            pass
        return "I'm thinking about that…"

    def _bring_ui_foreground(self) -> None:
        if not self.ui:
            return
        root = getattr(self.ui, "root", None)
        if root:
            try:
                root.deiconify(); root.lift(); root.focus_force()
            except Exception:
                pass



# services/wake_word.py
from __future__ import annotations
import os
import threading
import time

try:
    import speech_recognition as sr
    _HAS_SR = True
except Exception:
    _HAS_SR = False


class WakeWordListener:
    """
    Lightweight speech-based wake-word listener for Jaicat.

    Usage patterns:
        WakeWordListener(callback=my_fn).start()
        WakeWordListener().start(my_fn)

    Default wake words:
        "jaicat", "jaycat", "jay cat", "jai cat"

    Environment variable override:
        set JAICAT_WAKE="hey jaicat"

    Notes:
        - Uses SpeechRecognition + Google recognizer (requires internet).
        - Consider swapping in Porcupine or Whisper later for offline use.
    """

    def __init__(
        self,
        callback=None,
        wake_words=None,
        lang: str = "en-GB",
        debug: bool = True,
    ):
        self._callback = callback
        self.lang = lang
        self.debug = debug
        self.listening = False
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

        # Build wake-word list
        custom_word = os.getenv("JAICAT_WAKE", "").strip().lower()
        base_words = wake_words or ["jaicat", "jaycat", "jay cat", "jai cat"]
        if custom_word and custom_word not in base_words:
            base_words.append(custom_word)
        self.wake_words = [w.lower() for w in base_words]

    # ---------- Public API ----------

    def start(self, on_wake_callback=None) -> bool:
        """
        Begin listening in a background thread.
        """
        if not _HAS_SR:
            if self.debug:
                print("[WakeWordListener] speech_recognition not available.")
            return False

        if on_wake_callback:
            self._callback = on_wake_callback
        if not callable(self._callback):
            if self.debug:
                print("[WakeWordListener] No valid callback provided.")
            return False

        if self._thread and self._thread.is_alive():
            return True  # already running

        self.listening = True
        self._stop.clear()
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        if self.debug:
            print("[WakeWordListener] Started listening thread.")
        return True

    def stop(self) -> None:
        """
        Stop listening.
        """
        self.listening = False
        self._stop.set()
        if self.debug:
            print("[WakeWordListener] Stopped listening thread.")

    # ---------- Internal Loop ----------

    def _listen_loop(self) -> None:
        if not _HAS_SR:
            return
        try:
            recognizer = sr.Recognizer()
            mic = sr.Microphone()
        except Exception as e:
            if self.debug:
                print(f"[WakeWordListener] Mic unavailable: {e}")
            return

        with mic as source:
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.6)
            except Exception:
                pass

        while not self._stop.is_set():
            try:
                with mic as source:
                    if self.debug:
                        print("[WakeWordListener] Listening...")
                    audio = recognizer.listen(source, phrase_time_limit=4, timeout=5)

                phrase = recognizer.recognize_google(audio, language=self.lang).lower()
                if self.debug:
                    print(f"[WakeWordListener] Heard: {phrase}")

                if any(w in phrase for w in self.wake_words):
                    if self.debug:
                        print("[WakeWordListener] Wake word matched!")
                    try:
                        self._callback()
                    except Exception as e:
                        if self.debug:
                            print(f"[WakeWordListener] Callback error: {e}")
                    time.sleep(1.5)  # brief cooldown

            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                if self.debug:
                    print("[WakeWordListener] Could not understand audio.")
                time.sleep(0.6)
            except Exception as e:
                if self.debug:
                    print(f"[WakeWordListener] Error: {e}")
                time.sleep(1.0)

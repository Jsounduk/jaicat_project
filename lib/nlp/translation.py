# lib/nlp/translation.py

from googletrans import Translator

class TranslationService:
    def __init__(self):
        self.translator = Translator()

    def translate_text(self, text, dest_language='en', src_language=None):
        """
        Translates the input text to the specified destination language.

        Parameters:
        - text: The text to translate.
        - dest_language: The target language to translate the text into (default is English).
        - src_language: The source language (optional).

        Returns:
        - Translated text.
        """
        try:
            translated = self.translator.translate(text, dest=dest_language, src=src_language)
            return translated.text
        except Exception as e:
            print(f"Error in translation: {e}")
            return None

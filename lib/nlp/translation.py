# lib/nlp/translation.py

from deep_translator import GoogleTranslator

class TranslationService:
    def __init__(self, source='auto', target='en'):
        self.source_lang = source
        self.target_lang = target

    def translate_text(self, text, dest_language=None, src_language=None):
        """
        Translates the input text to the specified destination language.

        Parameters:
        - text: The text to translate.
        - dest_language: The target language to translate the text into (default is from init or 'en').
        - src_language: The source language (default is 'auto').

        Returns:
        - Translated text.
        """
        try:
            translated = GoogleTranslator(
                source=src_language or self.source_lang,
                target=dest_language or self.target_lang
            ).translate(text)
            return translated
        except Exception as e:
            print(f"🛑 Error in translation: {e}")
            return None

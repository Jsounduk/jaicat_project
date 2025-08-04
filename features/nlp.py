import spacy
import psutil
import subprocess
import importlib.util

class NLPSystem:
    def __init__(self):
        self.nlp = None
        self.load_nlp_model()

    def load_nlp_model(self):
        required_mb = 600  # Minimum RAM for 'en_core_web_lg'
        available_mb = psutil.virtual_memory().available / (1024 ** 2)

        # Try loading the large SpaCy model if memory allows
        if available_mb > required_mb:
            try:
                print("[INFO] Trying to load 'en_core_web_lg'...")
                self.nlp = spacy.load("en_core_web_lg")
                print("[INFO] Loaded 'en_core_web_lg'.")
            except Exception as e:
                print(f"[WARNING] Could not load 'en_core_web_lg': {e}")

        # Fallback to small model
        if self.nlp is None:
            try:
                print("[INFO] Falling back to 'en_core_web_sm'...")
                if not self._is_model_installed("en_core_web_sm"):
                    print("[INFO] Downloading 'en_core_web_sm'...")
                    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
                self.nlp = spacy.load("en_core_web_sm")
                print("[INFO] Loaded 'en_core_web_sm'.")
            except Exception as e:
                raise RuntimeError(f"[ERROR] Failed to load any SpaCy model: {e}")

    def _is_model_installed(self, model_name):
        spec = importlib.util.find_spec(model_name)
        return spec is not None

    def analyze_text(self, text):
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

    def part_of_speech_tagging(self, text):
        doc = self.nlp(text)
        return [(token.text, token.pos_) for token in doc]

    def extract_keywords(self, text):
        doc = self.nlp(text)
        return [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]

    def summarize_text(self, text, max_sentences=2):
        doc = self.nlp(text)
        sentences = list(doc.sents)
        return " ".join([sent.text for sent in sentences[:max_sentences]])

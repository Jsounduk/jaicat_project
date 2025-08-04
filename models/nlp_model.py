import spacy

class NLPModel:
    def __init__(self, model_name="en_core_web_sm"):
        self.model_name = model_name
        self.nlp = None

    def load_model(self):
        self.nlp = spacy.load(self.model_name)

    def process_text(self, text, entity_types=None):
        try:
            if not self.nlp:
                self.load_model()
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Invalid input text")
            doc = self.nlp(text)
            if entity_types:
                entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in entity_types]
            else:
                entities = [(ent.text, ent.label_) for ent in doc.ents]
            return entities
        except Exception as e:
            return {"error": str(e)}

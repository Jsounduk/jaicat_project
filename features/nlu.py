import spacy
from spacy import displacy

class NLU:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def extract_intent_and_entities(self, user_input):
        try:
            doc = self.nlp(user_input)
            intent = self.detect_intent(doc)
            entities = self.extract_entities(doc)
            return {"intent": intent, "entities": entities}
        except Exception as e:
            return {"error": str(e)}

    def detect_intent(self, doc):
        # Implement intent detection logic here
        # For example, you can use spaCy's entity recognition to identify intents
        intent_entities = [ent.text for ent in doc.ents if ent.label_ == "INTENT"]
        if intent_entities:
            return intent_entities[0]
        else:
            return None

    def extract_entities(self, doc):
        # Implement entity recognition logic here
        # For example, you can use spaCy's entity recognition to extract entities
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

    def visualize_entities(self, doc):
        # Visualize entities using spaCy's displacy
        displacy.render(doc, style="ent")

# Test the code
nlu = NLU()
user_input = "I want to book a flight from New York to Los Angeles"
result = nlu.extract_intent_and_entities(user_input)
print(result)

# Visualize entities
nlu.visualize_entities(nlu.nlp(user_input))
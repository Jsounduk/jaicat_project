import spacy
from transformers import pipeline

class NLU:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.labels = [
            "question",
            "greet",
            "goodbye",
            "shut_down",
            "generate_code",
            "analyze_text",
            "analyze_sentiment",
            "capture_image",
            "start_recording",
            "add_task",
            "create_project",
            "complete_project",
            "list_projects",
            "get_nutrition",
            "find_recipes",
            "get_recipe_instructions"
        ]

    def extract_intent_and_entities(self, user_input):
        try:
            result = self.classifier(user_input, self.labels)
            intent = result["labels"][0]
        except Exception as e:
            print(f"[ERROR] Intent classification failed: {e}")
            intent = None

        entities = self.extract_entities(user_input)
        return {"intent": intent, "entities": entities}

    def extract_entities(self, text):
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]
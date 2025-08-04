# conversation/dialogue_manager.py

from conversation.nlu import NLU
from features.nlp import NLPSystem
from conversation.nlg import ContextualResponder
from transformers import pipeline
import wikipedia
import logging

logging.basicConfig(level=logging.INFO)

class DialogueManager:
    def __init__(self):
        self.nlu = NLU()
        self.nlp_system = NLPSystem()
        self.contextual_responder = ContextualResponder()
        self.context = {}

        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    def handle_question(self, question):
        logging.info(f"[QUESTION] {question}")
        answer = self.get_answer(question)

        if answer:
            return answer
        else:
            return self.contextual_responder.generate_response(question, self.context)

    def get_answer(self, question):
        try:
            # Classify the type of question (optional, for future routing)
            labels = ["factual question", "personal query", "open-ended", "command"]
            result = self.classifier(question, labels)
            logging.info(f"[CLASSIFICATION] {result}")

            # Try Wikipedia
            return wikipedia.summary(question, sentences=2)

        except wikipedia.exceptions.DisambiguationError as e:
            return "Could you please be more specific? I found multiple results for that question."

        except wikipedia.exceptions.PageError:
            return "Sorry, I couldn't find anything about that."

        except Exception as e:
            logging.warning(f"[Wikipedia FAIL] {e}")
            return None

    def process_user_input(self, user_input):
        extracted_data = self.nlu.extract_intent_and_entities(user_input)
        intent = extracted_data.get("intent")
        entities = extracted_data.get("entities")

        logging.info(f"[INTENT] {intent} | [ENTITIES] {entities}")

        if intent in ("question", "ask", "query"):
            return self.handle_question(user_input)

        elif intent == "greet":
            return self.greet()

        elif intent == "goodbye":
            return self.goodbye()

        elif intent == "play_music":
            return "Sure! Playing your favourite playlist now."

        elif intent == "generate_code":
            return self.generate_code(entities)

        elif intent == "analyze_sentiment":
            return self.analyze_sentiment(entities)

        else:
            return self.contextual_responder.generate_response(user_input, self.context)

    def greet(self):
        return "Hey there! What can I help you with today?"

    def goodbye(self):
        return "Goodbye for now. See you soon!"

    def generate_code(self, entities):
        return "Code generation is enabled for admin only. Please verify identity."

    def analyze_sentiment(self, entities):
        return self.nlp_system.analyze_sentiment(entities.get("text", ""))

import logging
import requests
from conversation.nlu import NLU
from features.nlp import NLPSystem

class DialogueManager:
    def __init__(self, nlu=None, nlp_system=None, contextual_responder=None):
        self.nlu = nlu or NLU()
        self.nlp_system = nlp_system or NLPSystem()
        self.contextual_responder = contextual_responder  # Optional fallback
        self.logger = logging.getLogger(__name__)
        self.ollama_url = "http://localhost:11434/api/generate"  # Ollama HTTP API endpoint

    def query_ollama(self, prompt):
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response", "Sorry, I didn’t get that 💋")
        except requests.RequestException as e:
            self.logger.error(f"[OLLAMA HTTP ERROR] {e}")
            return "Something went wrong trying to answer that. Maybe rephrase it for me?"

    def process_user_input(self, user_input):
        extracted = self.nlu.extract_intent_and_entities(user_input)
        intent = extracted.get("intent")
        entities = extracted.get("entities", [])

        self.logger.info(f"[INTENT] {intent} | [ENTITIES] {entities}")

        if intent == "greet":
            return "Hello! How can I assist you today?"
        elif intent == "goodbye":
            return "Goodbye! Have a great day!"
        elif intent == "shut_down":
            return "shutdown_now"
        elif intent == "generate_code":
            return self.nlp_system.generate_code("sample")
        elif intent == "analyze_text":
            return self.nlp_system.analyze_text(user_input)
        elif intent == "analyze_sentiment":
            return self.nlp_system.analyze_sentiment(user_input)
        elif intent == "question":
            return self.handle_question(user_input)
        else:
            return self.query_ollama(user_input)

    def handle_question(self, question):
        self.logger.info(f"[QUESTION] {question}")
        return self.query_ollama(question)

    def shutdown(self):
        return "shutdown_now"

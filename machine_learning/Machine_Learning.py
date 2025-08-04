import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import spacy
import tensorflow as tf
from tensorflow import Sequential
from tensorflow import LSTM, Dense

# Load the necessary models
nlp = spacy.load("en_core_web_sm")

# Intent Detection
class IntentDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression()

    def add_training_example(input_text, intent):
        """Adds a new training example to the model."""
        # This method would typically update the training data and retrain the model
        pass

    def train(self, intent_data):
        X = intent_data["input"]
        y = intent_data["intent"]
        X_vec = self.vectorizer.fit_transform(X)
        self.model.fit(X_vec, y)

    def evaluate(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print("Accuracy:", accuracy)

    def predict(self, input_text):
        input_vec = self.vectorizer.transform([input_text])
        return self.model.predict(input_vec)

# Entity Recognition
class EntityRecognizer:
    def __init__(self):
        pass

    def extract_entities(self, input_text):
        doc = nlp(input_text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

# Contextual Response Generation
class ResponseGenerator:
    def __init__(self):
        self.model = Sequential()
        self.model.add(LSTM(64, input_shape=(1, 1)))
        self.model.add(Dense(64, activation="relu"))
        self.model.add(Dense(1, activation="sigmoid"))
        self.model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])

    def train(self, response_data):
        X = response_data["context"]
        y = response_data["response"]
        X_vec = tf.convert_to_tensor([X])
        y_vec = tf.convert_to_tensor([y])
        self.model.fit(X_vec, y_vec, epochs=10)

    def generate_response(self, context, input_text):
        context_vec = tf.convert_to_tensor([context])
        input_vec = tf.convert_to_tensor([input_text])
        output = self.model.predict(context_vec, input_vec)
        return output

# Main function
def main():
    # Load the datasets
    intent_data = pd.read_csv("intent_data.csv")
    entity_data = pd.read_csv("entity_data.csv")
    response_data = pd.read_csv("response_data.csv")

    # Create instances of the classes
    intent_detector = IntentDetector()
    entity_recognizer = EntityRecognizer()
    response_generator = ResponseGenerator()

    # Train the models
    intent_detector.train(intent_data)
    response_generator.train(response_data)

    # Evaluate the models
    X_test = intent_data["input"].iloc[100:]
    y_test = intent_data["intent"].iloc[100:]
    X_test_vec = intent_detector.vectorizer.transform(X_test)
    intent_detector.evaluate(X_test_vec, y_test)

    # Test the models
    input_text = "Turn on the living room lights"
    intent = intent_detector.predict(input_text)
    entities = entity_recognizer.extract_entities(input_text)
    response = response_generator.generate_response("context", input_text)

    print("Intent:", intent)
    print("Entities:", entities)
    print("Response:", response)

if __name__ == "__main__":
    main()
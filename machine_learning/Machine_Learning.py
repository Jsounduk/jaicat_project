import os
import json
import pandas as pd
import spacy
import tensorflow as tf
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.utils import to_categorical

# === Load spaCy NLP ===
nlp = spacy.load("en_core_web_sm")

# === INTENT DETECTION ===
class IntentDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression()

    def train(self, intent_data):
        X = intent_data["input"]
        y = intent_data["intent"]
        X_vec = self.vectorizer.fit_transform(X)
        self.model.fit(X_vec, y)

    def evaluate(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print("ðŸ§ª Intent Accuracy:", accuracy)

    def predict(self, input_text):
        input_vec = self.vectorizer.transform([input_text])
        return self.model.predict(input_vec)

# === ENTITY RECOGNITION ===
class EntityRecognizer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def train(self, entity_data):    
        # This method would typically update the training data and retrain the model
        # However, since we're using a pre-trained model, we don't need to do anything
        pass

    def extract_entities(self, input_text):
        doc = nlp(input_text)
        return [(ent.text, ent.label_) for ent in doc.ents]

# === RESPONSE GENERATOR (with safety) ===
class ResponseGenerator:
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()

    def train(self, response_data):
        X = response_data["context"]
        y = response_data["response"]

        # Encode responses into numerical labels
        y_encoded = self.label_encoder.fit_transform(y)
        num_classes = len(set(y_encoded))
        y_vec = to_categorical(y_encoded, num_classes)

        # Dummy input (weâ€™ll use index for training simplicity)
        X_vec = tf.convert_to_tensor([[i] for i in range(len(X))], dtype=tf.float32)

        # Build model
        self.model = Sequential()
        self.model.add(tf.keras.Input(shape=(1,)))
        self.model.add(Dense(64, activation="relu"))
        self.model.add(Dense(num_classes, activation="softmax"))
        self.model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

        # Train model
        self.model.fit(X_vec, y_vec, epochs=10)

    def generate_response(self, context, input_text):
        try:
            idx = self.label_encoder.transform([context])[0]
            input_vec = tf.convert_to_tensor([[idx]], dtype=tf.float32)
            prediction = self.model.predict(input_vec)
            response_idx = prediction.argmax()
            return self.label_encoder.inverse_transform([response_idx])[0]
        except Exception as e:
            print(f"âŒ Unknown or invalid context: {context} â€” {e}")
            return "Sorry babe, I donâ€™t know how to respond to that yet ðŸ˜¢"


# === TAG SORTER ===
class TagSorter:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression()
        self.is_trained = False

    def train_from_log(self, log_path):
        with open(log_path, 'r') as f:
            log_data = json.load(f)

        tag_texts, folders = [], []
        for entry in log_data:
            tags = entry['tags']
            folder_path = os.path.dirname(entry['image'])
            tag_texts.append(' '.join(tags))
            folders.append(folder_path)

        if tag_texts:
            X = self.vectorizer.fit_transform(tag_texts)
            y = folders
            self.model.fit(X, y)
            self.is_trained = True
            print(f"âœ… TagSorter trained on {len(tag_texts)} examples.")

    def predict_folder(self, tags):
        if not self.is_trained:
            raise Exception("Model not trained. Call train_from_log() first.")
        tag_str = ' '.join(tags)
        X_test = self.vectorizer.transform([tag_str])
        prediction = self.model.predict(X_test)
        return prediction[0]

# === LOG IMAGE TAGGING ===
def log_to_machine_learning(image_path, final_tags):
    log_path = "services/media_management/tag_learning_log.json"
    entry = {
        "image": image_path,
        "tags": final_tags,
        "timestamp": datetime.now().isoformat()
    }

    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []

    data.append(entry)
    with open(log_path, 'w') as f:
        json.dump(data, f, indent=2)

# === MAIN ===
def main():
    # Load datasets
    intent_data = pd.read_csv("machine_learning/intent_data.csv")
    entity_data = pd.read_csv("machine_learning/entity_data.csv")
    response_data = pd.read_csv("machine_learning/response_data.csv")

    # Create instances
    intent_detector = IntentDetector()
    entity_recognizer = EntityRecognizer()
    response_generator = ResponseGenerator()

    # Train models
    intent_detector.train(intent_data)
    response_generator.train(response_data)

    # Evaluate intent accuracy
    X_test = intent_data["input"].iloc[100:]
    y_test = intent_data["intent"].iloc[100:]
    X_test_vec = intent_detector.vectorizer.transform(X_test)
    intent_detector.evaluate(X_test_vec, y_test)

    # Predict
    input_text = "Turn on the light"
    intent = intent_detector.predict(input_text)[0]
    entities = entity_recognizer.extract_entities(input_text)
    response = response_generator.generate_response(intent, input_text)

    print("ðŸ§  Intent:", intent)
    print("ðŸ” Entities:", entities)
    print("ðŸ’¬ Response:", response)

    # Optional: Train TagSorter
    if os.path.exists("services/media_management/tag_learning_log.json"):
        sorter = TagSorter()
        try:
            sorter.train_from_log("services/media_management/tag_learning_log.json")
        except Exception as e:
            print("âš ï¸ TagSorter training error:", e)

if __name__ == "__main__":
    main()

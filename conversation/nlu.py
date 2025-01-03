import spacy
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

class NLU:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.vectorizer = TfidfVectorizer()  # Define vectorizer here
        self.intent_model = self.train_intent_model()
        
    def train_intent_model(self):
        """Train the intent classification model."""
        # Load the dataset
        intent_data = pd.read_csv("intent_data.csv")  # Load the intent data

        # Preprocess the data
        X = self.vectorizer.fit_transform(intent_data["input_text"])  # Use self.vectorizer here
        y = intent_data["intent"]

        # Train the model
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(X, y)
        return clf

    def extract_intent_and_entities(self, user_input):
        """Extract intent and entities from user input."""
        intent = self.predict_intent(user_input)
        entities = self.extract_entities(user_input)

        return {
            "intent": intent,
            "entities": entities
        }

    def predict_intent(self, input_text):
        """Predict intent based on the input text."""
        input_vector = self.vectorizer.transform([input_text])  # Use self.vectorizer here
        return self.intent_model.predict(input_vector)[0]

    def extract_entities(self, input_text):
        """Extract entities from the input text using SpaCy."""
        doc = self.nlp(input_text)
        return [(ent.text, ent.label_) for ent in doc.ents]

# If you want to keep standalone functions for intent and entity extraction, here they are:

def extract_intent(text):
    """Extract the intent from the input text."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    intent = ""
    for token in doc:
        if token.dep_ == "ROOT":
            intent = token.text
            break
    return intent

def extract_entities(text):
    """Extract entities from the input text."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))
    return entities

def extract_intent_and_entities(self, user_input):
    doc = self.nlp(user_input)
    
    # Extract intent (e.g., "get_travel_recommendations")
    intent = "get_travel_recommendations" if "travel" in user_input and "recommendations" in user_input else None
    intent = "capture_image" if "capture" in user_input and "image" in user_input else None
    # Extract entities (e.g., category)
    entities = {}
    if intent:
        for token in doc:
            if token.text in self.destinations:  # Check if the token matches any category
                entities['category'] = token.text
    if "create project" in user_input:
            return {
                "intent": "create_project",
                "entities": {"project_name": user_input.replace("create project", "").strip()}
            }
    elif "add task" in user_input:
            return {
                "intent": "add_task",
                "entities": {
                    "project_name": user_input.split("in")[-1].strip(),
                    "task": user_input.replace("add task", "").split("in")[0].strip()
                }
            }
    elif "list projects" in user_input:
            return {"intent": "list_projects", "entities": {}}
    elif "complete project" in user_input:
            return {
                "intent": "complete_project",
                "entities": {"project_name": user_input.replace("complete project", "").strip()}
            }
    
    if "capture image" in user_input:
        return {"intent": "capture_image", "entities": {}}
    
    if "get camera status" in user_input:
        return {"intent": "get_camera_status", "entities": {}}
    elif "capture snapshot" in user_input:
        camera_id = extract_camera_id(user_input)  # Implement a method to extract camera_id
        return {"intent": "capture_snapshot", "entities": {"camera_id": camera_id}}
    elif "start recording" in user_input:
        camera_id = extract_camera_id(user_input)
        return {"intent": "start_recording", "entities": {"camera_id": camera_id}}
    elif "stop recording" in user_input:
        camera_id = extract_camera_id(user_input)
        return {"intent": "stop_recording", "entities": {"camera_id": camera_id}}
    if "capture snapshot" in user_input:
        return {"intent": "capture_snapshot", "entities": {}}
    elif "start recording" in user_input:
        return {"intent": "start_recording", "entities": {}}
    elif "stop recording" in user_input:
        return {"intent": "stop_recording", "entities": {}}
    if "nutrition facts" in user_input:
        return {"intent": "get_nutrition", "entities": {"food_item": user_input.split("nutrition facts")[-1].strip()}}
    elif "find recipes" in user_input:
        return {"intent": "find_recipes", "entities": {"ingredient": user_input.split("find recipes")[-1].strip()}}
    elif "recipe instructions" in user_input:
        return {"intent": "get_recipe_instructions", "entities": {"recipe_id": user_input.split("recipe instructions")[-1].strip()}}
    if "analyze file" in user_input:
        return {"intent": "analyze_file", "entities": {"file_path": user_input.split("analyze file")[-1].strip()}}
    
    
    return {"intent": intent, "entities": entities}
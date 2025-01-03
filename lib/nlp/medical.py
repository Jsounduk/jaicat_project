# lib/nlp/medical.py

import spacy

class MedicalNLP:
    def __init__(self, model='en_core_web_sm'):
        # Load the SpaCy language model
        self.nlp = spacy.load(model)

    def extract_medical_entities(self, text):
        """
        Extract medical-related entities from the input text.
        
        Parameters:
        - text: The medical text to analyze.

        Returns:
        - A list of tuples containing the entity text and its label.
        """
        doc = self.nlp(text)
        medical_entities = []
        
        for ent in doc.ents:
            if ent.label_ in ["DISEASE", "SYMPTOM", "MEDICATION", "TREATMENT"]:
                medical_entities.append((ent.text, ent.label_))
        
        return medical_entities

    def classify_symptoms(self, symptoms):
        """
        Classify the input symptoms into categories.
        
        Parameters:
        - symptoms: A list of symptom strings to classify.

        Returns:
        - A dictionary categorizing symptoms.
        """
        symptom_categories = {
            "Respiratory": [],
            "Gastrointestinal": [],
            "Neurological": [],
            "Cardiovascular": [],
            "Others": []
        }

        for symptom in symptoms:
            # Simple keyword matching for classification (this could be replaced with a more sophisticated model)
            if "cough" in symptom or "breath" in symptom:
                symptom_categories["Respiratory"].append(symptom)
            elif "nausea" in symptom or "vomit" in symptom:
                symptom_categories["Gastrointestinal"].append(symptom)
            elif "headache" in symptom:
                symptom_categories["Neurological"].append(symptom)
            elif "chest pain" in symptom:
                symptom_categories["Cardiovascular"].append(symptom)
            else:
                symptom_categories["Others"].append(symptom)
        
        return symptom_categories

    def analyze_medical_text(self, text):
        """
        Analyze the input medical text for entities and symptoms.
        
        Parameters:
        - text: The medical text to analyze.

        Returns:
        - A dictionary containing extracted entities and categorized symptoms.
        """
        entities = self.extract_medical_entities(text)
        symptoms = [ent[0] for ent in entities if ent[1] == "SYMPTOM"]
        symptom_classification = self.classify_symptoms(symptoms)

        return {
            'entities': entities,
            'symptom_classification': symptom_classification
        }

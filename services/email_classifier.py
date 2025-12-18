class EmailClassifier:
    def __init__(self, nlp, classifier_model):
        self.nlp = nlp
        self.classifier = classifier_model  # assumes .predict(text) returns a class

    def classify_email(self, email):
        """
        Classifies the urgency of an email based on its subject + snippet.
        Returns: ('urgent' | 'important' | 'ignore')
        """
        text = f"{email['subject']} {email['snippet']}".lower()
        sentiment = self.nlp.analyze_sentiment(text)
        category = self.classifier.predict(text)

        # Heuristics to override dumb classifier
        if "missed" in text or "urgent" in text or "invoice" in text:
            category = "urgent"
        elif "booking" in text or "payment" in text:
            category = "important"
        elif "unsubscribe" in text or "promotion" in text:
            category = "ignore"

        return category

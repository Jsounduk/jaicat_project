from transformers import pipeline

class TextClassificationModel:
    def __init__(self, model_name="sentiment-analysis"):
        self.model_name = model_name
        self.classifier = None

    def load_model(self):
        
        self.classifier = pipeline(self.model_name)

    def classify_text(self, text):
        try:
            if not self.classifier:
                self.load_model()
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Invalid input text")
            result = self.classifier(text)
            return self._parse_output(result)
        except Exception as e:
            return {"error": str(e)}

    def _parse_output(self, output):
        # Parse the output to return a more readable result
        # For example, return a dictionary with the sentiment label and score
        return {"sentiment": output[0]["label"], "score": output[0]["score"]}

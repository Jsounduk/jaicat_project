class NLPSystem:
    def analyze_sentiment(self, text):
        text = text.lower()
        if any(word in text for word in ["love", "great", "awesome", "cool"]):
            return "happy"
        elif any(word in text for word in ["sad", "depressed", "tired", "angry"]):
            return "sad"
        elif "sexy" in text or "flirt" in text:
            return "flirty"
        return "neutral"

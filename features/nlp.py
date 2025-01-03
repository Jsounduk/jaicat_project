import torch
import spacy
from transformers import BertTokenizer, BertForSequenceClassification

class NLPSystem:
    def __init__(self):
        # Load the SpaCy language model
        self.nlp = spacy.load('en_core_web_lg')

        # Initialize sentiment analysis using BERT
        self.sentiment_analysis_model = SentimentAnalysis()

    def analyze_text(self, text):
        """Analyze text to extract named entities."""
        doc = self.nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

    def part_of_speech_tagging(self, text):
        """Perform part-of-speech tagging on the input text."""
        doc = self.nlp(text)
        pos_tags = [(token.text, token.pos_) for token in doc]
        return pos_tags

    def language_detection(self, text):
        """Detect the language of the input text."""
        lang = self.nlp(text)._.language
        return "English" if lang == 'en' else 'Unknown'

    def text_summarization(self, text, max_length=100):
        """Summarize the input text (placeholder for future implementation)."""
        # Summarization logic to be added, possibly using transformers
        pass

    def process(self, command):
        """Process user commands for different NLP tasks."""
        command = command.lower()
        
        if "analyze text" in command:
            text = command.replace("analyze text", "").strip()
            entities = self.analyze_text(text)
            return f"Entities found: {entities}"
        
        elif "analyze sentiment" in command:
            text = command.replace("analyze sentiment", "").strip()
            sentiment = self.sentiment_analysis_model.analyze_sentiment(text)
            return f"Sentiment: {sentiment}"
        
        elif "part of speech tagging" in command:
            text = command.replace("part of speech tagging", "").strip()
            pos_tags = self.part_of_speech_tagging(text)
            return f"Part of Speech Tagging: {pos_tags}"

        # Add other NLP-related tasks here, like summarization, translation, etc.
        return "Unknown command. Please try again."

class SentimentAnalysis:
    def __init__(self, model_name="nlptown/bert-base-multilingual-uncased-sentiment"):
        """Initialize BERT model for sentiment analysis."""
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name)

    def analyze_sentiment(self, text):
        """Analyze sentiment using BERT sentiment model."""
        inputs = self.tokenizer.encode_plus(text, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)

        # Apply softmax to get probabilities
        scores = torch.nn.functional.softmax(outputs.logits, dim=1)
        
        # Sentiment is determined by the highest score
        sentiment = torch.argmax(scores).item()
        
        if sentiment >= 4:
            return "positive"
        elif sentiment <= 1:
            return "negative"
        else:
            return "neutral"

# In features/nlp.py

import spacy
import torch
from transformers import BertTokenizer, BertForSequenceClassification

class NLPSystem:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_lg')
        self.sentiment_analysis = SentimentAnalysis()

    def analyze_text(self, text):
        try:
            doc = self.nlp(text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            return entities
        except Exception as e:
            return f"Error: {e}"

    def part_of_speech_tagging(self, text):
        try:
            doc = self.nlp(text)
            pos_tags = [(token.text, token.pos_) for token in doc]
            return pos_tags
        except Exception as e:
            return f"Error: {e}"

    def language_detection(self, text):
        lang = self.nlp(text)._language
        return "English" if lang == 'en' else 'Unknown'

    def text_summarization(self, text, max_length):
        try:
            model_name = "bert-base-uncased"
            tokenizer = BertTokenizer.from_pretrained(model_name)
            model = BertForSequenceClassification.from_pretrained(model_name)

            inputs = tokenizer.encode_plus(
                text,
                max_length=max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )

            input_ids = inputs["input_ids"].unsqueeze(0)
            attention_mask = inputs["attention_mask"].unsqueeze(0)

            with torch.no_grad():
                outputs = model(input_ids, attention_mask=attention_mask)
                hidden_states = outputs.hidden_states

            last_layer_output = hidden_states[-1][0]
            importance_scores = torch.sum(last_layer_output * attention_mask[0], dim=1)
            sorted_indices = torch.argsort(importance_scores, descending=True)

            summary = ""
            for sentence_idx in sorted_indices:
                summary += tokenizer.convert_ids_to_tokens(input_ids[0, sentence_idx].tolist())[1:-1] + " "
                if len(summary) > max_length:
                    break

            return summary.strip()

        except Exception as e:
            return f"Error: {e}"

    def process(self, command):
        command = command.lower()

        if "what is" in command or "how to" in command or "who" in command:
            response = self.ask_question(command)
            return response

        if "analyze text" in command:
            text = command.replace("analyze text", "").strip()
            entities = self.analyze_text(text)
            return f"Entities found: {entities}"
        
        elif "sentiment" in command:
            text = command.replace("analyze sentiment", "").strip()
            sentiment = self.sentiment_analysis.live_test(text)
            return f"Sentiment: {sentiment}"
        
        elif "part of speech tagging" in command:
            text = command.replace("part of speech tagging", "").strip()
            pos_tags = self.part_of_speech_tagging(text)
            return f"Part of Speech Tagging: {pos_tags}"
        
        elif "language detection" in command:
            text = command.replace("language detection", "").strip()
            language = self.language_detection(text)
            return f"Language: {language}"
        
        elif "text summarization" in command:
            text = command.replace("text summarization", "").strip()
            summary = self.text_summarization(text, 100)
            return f"Summary: {summary}"
        
        elif "generate code" in command:
            prompt = command.replace("generate code", "").strip()
            generated_code = self.code_generation_model.generate_code(prompt)
            return f"Generated code: {generated_code}"
        
        # Add more command processing as needed
        return "Command not recognized."

class SentimentAnalysis:
    def __init__(self, model_name="bert-base-uncased"):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

    def preprocess_text(self, text):
        try:
            inputs = self.tokenizer.encode_plus(
                text,
                add_special_tokens=True,
                max_length=512,
                return_attention_mask=True,
                return_tensors="pt"
            )
            return inputs
        except Exception as e:
            return f"Error: {e}"

    def analyze_sentiment(self, text):
        try:
            inputs = self.preprocess_text(text)
            outputs = self.model(**inputs)
            logits = outputs.logits
            sentiment = torch.argmax(logits)
            return sentiment.item()
        except Exception as e:
            return f"Error: {e}"

    def live_test(self, text):
        sentiment = self.analyze_sentiment(text)
        return "Positive" if sentiment == 1 else "Negative"

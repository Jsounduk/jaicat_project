from transformers import BartForConditionalGeneration, BartTokenizer
from datetime import datetime
import json
import os
import random

class ContextualResponder:
    def __init__(self):
        self.model = BartForConditionalGeneration.from_pretrained("facebook/bart-base")
        self.tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")

    def respond(self, context, input_text):
        prompt = f"{context} {input_text}".strip()
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        output = self.model.generate(**inputs, max_length=100)
        return self.tokenizer.decode(output[0], skip_special_tokens=True)
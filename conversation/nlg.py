from transformers import BartForConditionalGeneration, BartTokenizer

class ContextualResponder:
    def __init__(self):
        self.model = BartForConditionalGeneration.from_pretrained("facebook/bart-base")
        self.tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")

    def generate_response(self, context, input_text):
        inputs = self.tokenizer.encode_plus(
            f"{context} {input_text}",
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding="max_length"
        )
        outputs = self.model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=100,
            num_beams=4,
            early_stopping=True
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def respond(self, context, input_text):
        return self.generate_response(context, input_text)

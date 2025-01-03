from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class CodeGenerationModel:
    def __init__(self, model_name="t5-small"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None

    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

    def generate_code(self, prompt, max_length=150, num_return_sequences=1):
        try:
            if not self.model:
                self.load_model()
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError("Invalid input prompt")
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            outputs = self.model.generate(inputs, max_length=max_length, num_return_sequences=num_return_sequences)
            return [self.tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
        except Exception as e:
            return {"error": str(e)}

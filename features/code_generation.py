import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class CodeGenerationModel:
    def __init__(self):
        # Load pre-trained models
        self.codebert_tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')
        self.codebert_model = AutoModelForSeq2SeqLM.from_pretrained('microsoft/codebert-base')
        
        self.bert_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = AutoModelForSeq2SeqLM.from_pretrained('bert-base-uncased')

    def generate_code_with_codebert(self, input_text):
        inputs = self.codebert_tokenizer.encode_plus(
            input_text,
            add_special_tokens=True,
            max_length=512,
            return_tensors='pt'
        )
        outputs = self.codebert_model.generate(inputs['input_ids'], attention_mask=inputs['attention_mask'])
        codebert_code = self.codebert_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return codebert_code

    def generate_code_with_blackbox(self, input_text):
        bert_inputs = self.bert_tokenizer.encode_plus(
            input_text,
            add_special_tokens=True,
            max_length=512,
            return_tensors='pt'
        )
        code_description = self.bert_tokenizer.decode(bert_inputs['input_ids'][0], skip_special_tokens=True)
        blackbox_code = self.blackbox_model.generate(code_description, language='python')
        return blackbox_code

    def ensemble_code(self, code1, code2):
        if code1 == code2:
            return code1
        else:
            return code1 + '\n' + code2

    def generate_code(self, input_text):
        # Generate code using CodeBERT
        codebert_code = self.generate_code_with_codebert(input_text)
        
        # Generate code using BERT with Blackbox
        blackbox_code = self.generate_code_with_blackbox(input_text)
        
        # Combine the outputs using an ensemble method
        ensemble_code = self.ensemble_code(codebert_code, blackbox_code)
        
        return ensemble_code

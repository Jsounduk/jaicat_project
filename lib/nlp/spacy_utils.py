# lib/nlp/spacy_utils.py

import spacy

class SpacyUtils:
    def __init__(self, model='en_core_web_sm'):
        # Load the SpaCy language model
        self.nlp = spacy.load(model)

    def tokenize(self, text):
        """
        Tokenizes the input text into words.
        
        Parameters:
        - text: The text to tokenize.

        Returns:
        - A list of tokens.
        """
        doc = self.nlp(text)
        return [token.text for token in doc]

    def get_entities(self, text):
        """
        Extracts named entities from the input text.
        
        Parameters:
        - text: The text to analyze.

        Returns:
        - A list of tuples containing the entity text and its label.
        """
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

    def get_pos_tags(self, text):
        """
        Extracts part-of-speech tags from the input text.
        
        Parameters:
        - text: The text to analyze.

        Returns:
        - A list of tuples containing the token text and its part-of-speech tag.
        """
        doc = self.nlp(text)
        return [(token.text, token.pos_) for token in doc]

    def get_sentence_boundaries(self, text):
        """
        Returns the sentence boundaries of the input text.
        
        Parameters:
        - text: The text to analyze.

        Returns:
        - A list of sentences.
        """
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents]

    def analyze_text(self, text):
        """
        Analyzes the input text and returns tokens, entities, and part-of-speech tags.
        
        Parameters:
        - text: The text to analyze.

        Returns:
        - A dictionary containing tokens, entities, and part-of-speech tags.
        """
        tokens = self.tokenize(text)
        entities = self.get_entities(text)
        pos_tags = self.get_pos_tags(text)
        return {
            'tokens': tokens,
            'entities': entities,
            'pos_tags': pos_tags
        }

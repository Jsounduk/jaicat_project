import nltk
nltk.download('stopwords')
import nltk
import spacy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from spacy import displacy

nlp = spacy.load("en_core_web_sm")

class TextProcessor:
    def __init__(self):
        pass

    def tokenize_text(self, text):
        """
        Tokenize a text into individual words
        """
        return word_tokenize(text)

    def remove_stopwords(self, tokens):
        """
        Remove stopwords from a list of tokens
        """
        stop_words = set(stopwords.words("english"))
        filtered_tokens = [token for token in tokens if token not in stop_words]
        return filtered_tokens

    def lemmatize_tokens(self, tokens):
        """
        Lemmatize a list of tokens
        """
        lemmatizer = WordNetLemmatizer()
        lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
        return lemmatized_tokens

    def perform_named_entity_recognition(self, text):
        """
        Perform named entity recognition on a text
        """
        doc = nlp(text)
        entities = [(entity.text, entity.label_) for entity in doc.ents]
        return entities

    def perform_part_of_speech_tagging(self, text):
        """
        Perform part-of-speech tagging on a text
        """
        doc = nlp(text)
        pos_tags = [(token.text, token.pos_) for token in doc]
        return pos_tags

    def perform_dependency_parsing(self, text):
        """
        Perform dependency parsing on a text
        """
        doc = nlp(text)
        dependencies = [(token.text, token.dep_, token.head.text, token.head.pos_) for token in doc]
        return dependencies

    def visualize_dependencies(self, text):
        """
        Visualize the dependencies of a text using spaCy's displacy
        """
        doc = nlp(text)
        displacy.render(doc, style="dep")

# Example usage:
if __name__ == "__main__":
    text_processor = TextProcessor()
    text = "The quick brown fox jumped over the lazy dog."
    tokens = text_processor.tokenize_text(text)
    filtered_tokens = text_processor.remove_stopwords(tokens)
    lemmatized_tokens = text_processor.lemmatize_tokens(filtered_tokens)
    entities = text_processor.perform_named_entity_recognition(text)
    pos_tags = text_processor.perform_part_of_speech_tagging(text)
    dependencies = text_processor.perform_dependency_parsing(text)
    text_processor.visualize_dependencies(text)

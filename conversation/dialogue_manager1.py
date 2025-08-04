# conversations/dialogue_manager.py

from features.nlu import NLU
from features.nlp import NLPSystem
from conversation.nlg import ContextualResponder
import random
import wikipedia
import nltk
nltk.download('punkt')

class DialogueManager:
    def __init__(self):
        self.nlu = NLU()
        self.nlp_system = NLPSystem()
        self.contextual_responder = ContextualResponder()
        self.context = {}  # To maintain context between interactions

    def get_answer(self, question):
        try:
            answer = wikipedia.summary(question, sentences=2)
            return answer
        except wikipedia.exceptions.DisambiguationError as e:
            return "Could you please be more specific? I found multiple results for that question."
        except wikipedia.exceptions.PageError:
            return "Sorry, I couldn't find any information on that topic."
        
    def handle_question(self, question):
        if question.startswith("how much does a "):
            entity = question.split(" ")[-1].lower()
            answer = self.get_answer(entity)
            return answer
        else:
            return "Sorry, I didn't understand that question."

    def process_user_input(self, user_input):
        # Step 1: Extract intent and entities
        extracted_data = self.nlu.extract_intent_and_entities(user_input)
        intent = extracted_data.get("intent")
        entities = extracted_data.get("entities")
        

        # Step 2: Handle the extracted intent
        if intent is None:
            return "I'm sorry, I didn't understand that. Could you please rephrase?"

        # Greeting and Goodbye Intents
        if intent == "greet":
            return self.greet()
        elif intent == "goodbye":
            return self.goodbye()

        # Custom Commands based on the user's input
        elif intent == "generate_code":
            return self.generate_code(entities)
        elif intent == "analyze_text":
            return self.analyze_text(entities)
        elif intent == "analyze_sentiment":
            return self.analyze_sentiment(entities)

        # Example of adding more custom commands
        elif intent == "turn_on_lights":
            return self.turn_on_lights()
        elif intent == "play_music":
            return self.play_music()
        elif intent == "help":
            return self.help()
        elif intent == "what_can_you_do":
            return self.what_can_you_do()
        elif intent == "tell_me_a_story":
            return self.tell_me_a_story()
        elif intent == "question":
            return self.handle_question(user_input)

        # Handle unknown intents
        else:
            return self.handle_unknown_intent()

    def greet(self):
        return random.choice(["Hello! How can I help you today?", "Hi there! What can I do for you?"])

    def goodbye(self):
        return random.choice(["Goodbye! Have a great day!", "See you later!"])

    def generate_code(self, entities):
        if "code_snippet" in entities:
            code_snippet = entities["code_snippet"]
            # Example: use your NLP system or code generation model
            generated_code = self.nlp_system.generate_code(code_snippet)
            return f"Here is the code I generated: {generated_code}"
        else:
            return "I need more details to generate code. Could you provide a specific request?"

    def analyze_text(self, entities):
        if "text_to_analyze" in entities:
            text_to_analyze = entities["text_to_analyze"]
            analysis_result = self.nlp_system.analyze_text(text_to_analyze)
            return f"The analysis result is: {analysis_result}"
        else:
            return "Please provide the text you want me to analyze."

    def analyze_sentiment(self, entities):
        if "text_to_analyze" in entities:
            text_to_analyze = entities["text_to_analyze"]
            sentiment_result = self.nlp_system.analyze_sentiment(text_to_analyze)
            return f"The sentiment analysis result is: {sentiment_result}"
        else:
            return "Please provide the text for sentiment analysis."

    def turn_on_lights(self):
        # Implement interaction with smart devices
        return random.choice(["Turning on the living room lights.", "Lights on!"])

    def play_music(self):
        # Implement interaction with a music service
        return random.choice(["Playing your favorite music.", "Starting your playlist now."])

    def help(self):
        return "I can help you with the following commands: greet, goodbye, generate_code, analyze_text, analyze_sentiment, turn_on_lights, play_music, help, what_can_you_do, tell_me_a_story."

    def what_can_you_do(self):
        return "I can perform the following tasks: generate code, analyze text, analyze sentiment, turn on lights, play music, and tell you a story."

    def tell_me_a_story(self):
        # Implement a story generation model or retrieve a story from a database
        story = "Once upon a time, there was a brave knight who slayed a dragon and saved the kingdom."
        return story

    def handle_unknown_intent(self):
        return "I'm not sure how to handle that. Can you try asking in a different way?"
    
    def detect_vehicle(self):
        """Trigger car detection and retrieval of vehicle data."""
        return "Starting vehicle detection..."

    # Add to intent recognition
    def process_user_input(self, user_input):
        extracted_data = self.nlu.extract_intent_and_entities(user_input)
        intent = extracted_data.get("intent")
        
        # Command mapping
        if intent == "detect_vehicle":
            return self.detect_vehicle()
        else:
            return self.handle_unknown_intent()
        
    def process_motorbike_intents(intent: str, entities: list):
        if intent == "add_motorbike":
            name = entities.get('motorbike_name', 'Unnamed Motorbike')
            registration = entities.get('registration', 'Unknown')
            # Add motorbike logic here, save to JSON or respond via UI
            return f"Motorbike {name} with registration {registration} added."

        if intent == "show_motorbike_info":
            # Logic to retrieve stored motorbike info
            return "Here are your motorbike details: [details]."

        if intent == "motorbike_surveillance":
            # Logic to start motorbike surveillance
            return "Starting motorbike surveillance."
        

    
    
    
    
    


######## **General Commands**

#1. `hello` / `hi` / `hey` - Activate the AI assistant
#2. `goodbye` / `bye` - Deactivate the AI assistant
#3. `help` - Display available commands and features
#4. `what can you do` - Display a list of available features and modules

#**NLP and NLG**

#1. `tell me a story` - Generate a short story using NLG
#2. `write a poem` - Generate a poem using NLG
#3. `translate [text]` - Translate text using Language Translation module
#4. `summarize [text]` - Summarize text using NLP module

#**Text Classification and Code Generation**

#1. `classify [text]` - Classify text using Text Classification module
#2. `generate code [prompt]` - Generate code using Code Generation module
#3. `explain [code]` - Explain code using Code Generation module

#**Knowledge Base and Web Scraping**

#1. `learn from [pdf/epub]` - Learn from a PDF or EPUB file using Knowledge Base module
#2. `scrape [website]` - Scrape data from a website using Web Scraping module
#3. `find [information]` - Find information using Knowledge Base module

#**Image and Video Analysis**

#1. `analyze image [image]` - Analyze an image using Image Analysis module
#2. `analyze video [video]` - Analyze a video using Video Analysis module

#**YouTube and Social Media**

#1. `analyze youtube [video]` - Analyze a YouTube video using YouTube Analysis module
#2. `post on [social media]` - Post on a social media platform using Social Media Post Generation module
#3. `monitor [social media]` - Monitor a social media platform using Social Media Monitor module

#**People Recognition and Contact Management**

#1. `recognize [person]` - Recognize a person using People Recognition module
#2. `import contacts` - Import contacts using Contact Recognition module

#**Engineering and Motorbike Understanding**

#1. `explain [engineering concept]` - Explain an engineering concept using Engineering Understanding module
#2. `diagnose [motorbike issue]` - Diagnose a motorbike issue using Motorbike and Engine Understanding module

#**Home Surveillance and Automation**

#1. `display camera feeds` - Display camera feeds using Home Surveillance module
#2. `control [smart device]` - Control a smart device using Smart Home Automation module

#**Medical and Fitness Analysis**

#1. `analyze [medical data]` - Analyze medical data using Medical Analysis module
#2. `track [fitness data]` - Track fitness data using Fitness Analysis module

#**Travel Planning and Recommendations**

#1. `plan trip [destination]` - Plan a trip using Travel Planning module
#2. `recommend [travel destination]` - Recommend a travel destination using Travel Recommendations module

#**Personal Finance and Education**

#1. `track [personal finance data]` - Track personal finance data using Personal Finance Management module
#2. `learn [subject]` - Learn a subject using Education and Learning module

#**Health and Wellness**

#1. `track [health data]` - Track health data using Health and Wellness module
#2. `recommend [health advice]` - Recommend health advice using Health and Wellness module

#**Save Conversation Data**

#1. `save conversation` - Save conversation data using Save Conversation Data module

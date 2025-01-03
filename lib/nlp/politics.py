import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
from spacy import displacy
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import PyPDF2
import requests
from bs4 import BeautifulSoup
import cv2
import sqlite3
from lib.nlp.nltk_utils import preprocess_data
from database.knowledge_graph import KnowledgeGraph
from conversation.nlu import extract_entities, extract_intent
from database.web_scraping import Webscraping

# Load the NLTK data needed for the task
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

# Load the Spacy model for English
nlp = spacy.load("en_core_web_sm")

class Politics:
    def __init__(self):
        self.data = []
        self.knowledge_graph = {}

    def collect_data(self):
        # Web scraping code here
        self.webscraping = Webscraping()
        return self.webscraping.collect_data()

    def preprocess_data(self, text):
        return preprocess_data(text)
    
    def recognize_entities(self, text):
        return extract_entities(text)

    def create_knowledge_graph(self):
        kg = KnowledgeGraph()
        return kg.create_knowledge_graph()

    def answer_questions(self, query):
            # Extract entities and intent from the query
            doc = nlp(query)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            intent = extract_intent(query)

            # Create a knowledge graph instance
            kg = KnowledgeGraph()

            # Use the knowledge graph to answer the question
            answer = kg.answer_question(entities, intent)

            return answer

    def display_info(self, info_type, info):
        # Display information code here
        if info_type == "pdf":
            self.display_pdf(info)
        elif info_type == "webpage":
            self.display_webpage(info)
        elif info_type == "image":
            self.display_image(info)
        elif info_type == "video":
            self.display_video(info)

    def display_pdf(self, pdf_file):
        # Display PDF code here
        pdf_file = filedialog.askopenfilename(title="Select PDF file", filetypes=[("PDF files", "*.pdf")])
        pdf_reader = PyPDF2.PdfFileReader(pdf_file)
        page = pdf_reader.getPage(0)
        text = page.extractText()
        self.display_text(text)

    def display_webpage(self, url):
        # Display webpage code here
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        self.display_text(text)

    def display_image(self, image_file):
        # Display image code here
        image_file = filedialog.askopenfilename(title="Select image file", filetypes=[("Image files", "*.jpg *.png")])
        image = Image.open(image_file)
        image_tk = ImageTk.PhotoImage(image)
        self.display_image_tk(image_tk)

    def display_video(self, video_file):
        # Display video code here
        video_file = filedialog.askopenfilename(title="Select video file", filetypes=[("Video files", "*.mp4")])
        cap = cv2.VideoCapture(video_file)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def display_text(self, text):
        # Display text code here
        root = tk.Tk()
        root.title("Text Display")
        text_box = tk.Text(root)
        text_box.pack()
        text_box.insert(tk.END, text)
        root.mainloop()

    def display_image_tk(self, image_tk):
        # Display image code here
        root = tk.Tk()
        root.title("Image Display")
        image_label = tk.Label(root, image=image_tk)
        image_label.pack()
        root.mainloop()

    def store_data(self, title, main_content):
        conn = sqlite3.connect('webscraping.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS webscraping (title TEXT, main_content TEXT)')
        c.execute('INSERT INTO webscraping (title, main_content) VALUES (?, ?)', (title, main_content))
        conn.commit()
        conn.close()

# Create an instance of the Politics class
politics = Politics()

 # Test the collect_data method
title, main_content = politics.collect_data()
print(title)
print(main_content)
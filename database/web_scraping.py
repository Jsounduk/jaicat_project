import requests
from bs4 import BeautifulSoup

# Define a function to scrape a website
def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract relevant information from the website
    title = soup.find('title').text
    paragraphs = [p.text for p in soup.find_all('p')]
    return title, paragraphs

class Politics:
    def collect_data(self):
        url = "https://www.example.com"
        try:
            title, paragraphs = scrape_website(url)
            return title, paragraphs
        except requests.exceptions.RequestException as e:
            print(f" Error: {e}")
            return None, None

# Create an instance of the Politics class
politics = Politics()

# Test the collect_data method
title, paragraphs = politics.collect_data()
print(title)
print(paragraphs)
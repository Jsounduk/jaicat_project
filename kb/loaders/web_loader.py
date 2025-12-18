import requests
from bs4 import BeautifulSoup
from readability import Document

def load_url(url):
    html = requests.get(url, timeout=15).text
    doc = Document(html)
    soup = BeautifulSoup(doc.summary(), "html.parser")
    text = soup.get_text(" ", strip=True)
    return [{"text": text, "source": url, "type":"web"}] if text.strip() else []

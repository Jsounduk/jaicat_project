from ebooklib import epub
from bs4 import BeautifulSoup

def load_epub(path):
    book = epub.read_epub(str(path))
    items = []
    for item in book.get_items_of_type(9):
        soup = BeautifulSoup(item.get_body_content(), "html.parser")
        t = soup.get_text(" ", strip=True)
        if t:
            items.append({"text": t, "source": str(path), "type":"epub"})
    return items

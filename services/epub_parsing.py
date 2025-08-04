import epub


def parse_epub(file_path):
    book = epub.read_epub(file_path)
    text = ''
    for item in book.get_items_of_type(epub.ITEM_DOCUMENT):
        text += item.get_content().decode('utf-8')
    return text

epub_file_path = "example.epub"
epub_text = parse_epub(epub_file_path)
print(epub_text)
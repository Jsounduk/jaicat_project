from PIL import Image
import pytesseract

def ocr_image(path):
    img = Image.open(path)
    text = pytesseract.image_to_string(img)
    return [{"text": text, "source": str(path), "type":"image"}] if text.strip() else []

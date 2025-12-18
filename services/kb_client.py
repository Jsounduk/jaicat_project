from scripts.kb_ask import ask_kb
def get_answer(query):
    try:
        return ask_kb(query)
    except Exception:
        return "Sorry, I don’t know that yet."
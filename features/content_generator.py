# features/content_generator.py

import requests

def generate_with_ollama(prompt, model="llama3"):
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    return r.json()["response"]

import os

# Mapped module names: python import → pip package
known_packages = {
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "PIL": "Pillow",
    "PyPDF2": "PyPDF2",
    "nltk": "nltk",
    "face_recognition": "face-recognition",
    "transformers": "transformers",
    "tensorflow": "tensorflow",
    "torch": "torch",
    "pygame": "pygame",
    "gtts": "gTTS",
    "pyttsx3": "pyttsx3",
    "googletrans": "googletrans==4.0.0rc1",
    "wikipedia": "wikipedia",
    "speech_recognition": "SpeechRecognition",
    "spotipy": "spotipy",
    "msal": "msal",
    "google-api-python-client": "google-api-python-client",
    "google-auth": "google-auth",
    "google-auth-oauthlib": "google-auth-oauthlib",
    "azure-ai-contentsafety": "azure-ai-contentsafety",
    "azure-core": "azure-core",
    "smbprotocol": "smbprotocol",
    "pyudev": "pyudev",
    "tweepy": "tweepy",
    "instapy": "instapy",
    "onnxruntime": "onnxruntime",
    "openai": "openai",
    "epub": "ebooklib",
}

# Missing/inferred from the report
raw_imports = [
    "cv2", "PyPDF2", "PIL", "argparse", "asyncio", "azure.ai.contentsafety",
    "azure.ai.contentsafety.models", "azure.core.credentials", "azure.core.exceptions",
    "bleak", "bs4", "cryptography.fernet", "csv", "datetime", "email.mime.multipart",
    "email.mime.text", "epub", "face_recognition", "geocoder", "google.auth",
    "google.auth.transport.requests", "google.oauth2", "google_auth_oauthlib.flow",
    "googleapiclient.discovery", "googleapiclient.errors", "googletrans", "gtts",
    "importlib.util", "instapy", "json", "math", "msal", "mysql.connector", "nltk",
    "nltk.corpus", "nltk.stem", "nltk.tokenize", "numpy", "onnxruntime", "openai", "os",
    "os.path", "pandas", "pickle", "platform", "psutil", "pyautogui", "pygame",
    "pytesseract", "pyttsx3", "pyudev", "random", "re", "requests", "sklearn.ensemble",
    "sklearn.feature_extraction.text", "sklearn.linear_model", "sklearn.metrics",
    "sklearn.model_selection", "sklearn.neighbors", "smbclient", "smtplib", "socket",
    "spacy", "speech_recognition", "spotipy", "spotipy.oauth2", "sqlite3", "subprocess",
    "tensorflow", "textwrap", "time", "tkinter", "torch", "torch.nn", "torch.optim",
    "torch.utils.data", "transformers", "tweepy", "unittest", "webbrowser",
    "wikipedia", "youtube_dl", "youtube_transcript_api"
]

deduped = sorted(set([r.split('.')[0] for r in raw_imports]))

with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("# 🧠 JAICAT requirements.txt – Auto-generated\n\n")
    for mod in deduped:
        if mod in known_packages:
            f.write(f"{known_packages[mod]}\n")
        else:
            f.write(f"# {mod} – ❓ unknown, check manually\n")

print("✅ requirements.txt generated!")

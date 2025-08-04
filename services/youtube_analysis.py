import cv2
import youtube_dl
import speech_recognition as sr
from transformers import pipeline
from gtts import gTTS
from pygame import mixer
import googleapiclient.discovery
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from bs4 import BeautifulSoup
import PyPDF2
from PIL import Image


class YouTubeAnalysis:
    def __init__(self):
        self.api_key = "AIzaSyCLDg-FMV7c2xFE2dvZ8vHImy97h2_-2qc"
        self.nlp_model = pipeline("sentiment-analysis")
        self.transcript_api = YouTubeTranscriptApi()

    def download_video(self, video_url):
        """Download the video from YouTube."""
        ydl_opts = {'format': 'best'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            # Return the downloaded video file path
            return ydl.prepare_filename(ydl.extract_info(video_url))

    def extract_audio(self, video_path):
        """Extract audio frames from the downloaded video."""
        audio = cv2.VideoCapture(video_path)
        audio_frames = []
        while True:
            ret, frame = audio.read()
            if not ret:
                break
            audio_frames.append(frame)
        audio.release()
        return audio_frames

    def transcribe_audio(self, audio_frames):
        """Transcribe audio frames to text using speech recognition."""
        r = sr.Recognizer()
        transcript = ""
        for frame in audio_frames:
            audio_data = sr.AudioData(frame, 16000, 2)
            try:
                transcript += r.recognize_google(audio_data, language="en-US") + " "
            except sr.UnknownValueError:
                continue  # Skip unrecognized audio frames
        return transcript.strip()

    def analyze_sentiment(self, transcript):
        """Analyze sentiment of the transcript."""
        return self.nlp_model(transcript)

    def generate_summary(self, transcript):
        """Generate a summary of the video."""
        return " ".join(transcript.split(". ")[:3])  # Example: Summarize to the first 3 sentences

    def speak_summary(self, summary):
        """Speak the generated summary."""
        tts = gTTS(text=summary, lang='en')
        tts.save("summary.mp3")
        mixer.init()
        mixer.music.load("summary.mp3")
        mixer.music.play()

    def analyze_youtube_video(self, video_id):
        """Retrieve video metadata and analyze."""
        youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=self.api_key)
        request = youtube.videos().list(part='snippet', id=video_id)
        response = request.execute()
        return response['items'][0]['snippet']

    def scrape_website(self, url):
        """Scrape content from a website."""
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def parse_pdf_file(self, file_path):
        """Parse text from a PDF file."""
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def analyze_image(self, image_path):
        """Analyze the given image (add specific analysis logic)."""
        image = Image.open(image_path)
        # Placeholder for actual image analysis logic
        return "Image analysis result"

# Example usage
if __name__ == "__main__":
    youtube_service = YouTubeAnalysis(api_key="YOUR_API_KEY")
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with your desired video URL
    video_path = youtube_service.download_video(video_url)
    audio_frames = youtube_service.extract_audio(video_path)
    transcript = youtube_service.transcribe_audio(audio_frames)
    sentiment = youtube_service.analyze_sentiment(transcript)
    summary = youtube_service.generate_summary(transcript)
    youtube_service.speak_summary(summary)
    metadata = youtube_service.analyze_youtube_video("VIDEO_ID_HERE")  # Replace with actual video ID
    print(metadata)

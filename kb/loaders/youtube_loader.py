from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

def video_id(url):
    m = re.search(r"(?:v=|/shorts/|/live/|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None

def load_youtube(url):
    vid = video_id(url)
    if not vid: return []
    try:
        segments = YouTubeTranscriptApi.get_transcript(vid, languages=['en'])
        text = " ".join(seg["text"] for seg in segments)
        return [{"text": text, "source": url, "type":"youtube"}] if text.strip() else []
    except (TranscriptsDisabled, NoTranscriptFound):
        return []  # you can add Whisper fallback if you want

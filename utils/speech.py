import pyttsx3

class Speech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 170)
        self.engine.setProperty('volume', 1.0)
        self.voice_profiles = self.engine.getProperty('voices')

    def speak(self, text):
        print(f"[speech] Speaking: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def set_voice_by_sentiment(self, mood):
        female_voices = [v for v in self.voice_profiles if "female" in v.name.lower()]
        male_voices = [v for v in self.voice_profiles if "male" in v.name.lower()]

        if mood == "happy":
            voice = female_voices[0] if female_voices else self.voice_profiles[0]
        elif mood == "sad":
            voice = male_voices[0] if male_voices else self.voice_profiles[1]
        elif mood == "flirty":
            voice = female_voices[-1] if female_voices else self.voice_profiles[0]
        else:
            voice = self.voice_profiles[0]

        self.engine.setProperty('voice', voice.id)
import os
import time
import platform
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyIntegration:
    def __init__(self):
        self.client_id = "088813c3e61b4c4eaec0ba035d3c398f"
        self.client_secret = "160ba7377f0e4260bc5d473538a54f1b"
        self.redirect_uri = "http://localhost:3000/auth/callback"
        self.scope = "user-modify-playback-state user-read-playback-state"

        self.sp_oauth = SpotifyOAuth(client_id=self.client_id,
                                     client_secret=self.client_secret,
                                     redirect_uri=self.redirect_uri,
                                     scope=self.scope)

        self.sp = spotipy.Spotify(auth_manager=self.sp_oauth)

    def launch_spotify(self):
        # Determine the operating system
        os_name = platform.system()

        # Launch Spotify based on the operating system
        if os_name == "Windows":
            # Launch Spotify on Windows
            os.system("start spotify")
        elif os_name == "Darwin":  # macOS
            # Launch Spotify on macOS
            os.system("open -a Spotify")
        else:  # Linux
            # Launch Spotify on Linux
            os.system("spotify &")

    def play_song(self, song_name):
        try:
            # Launch Spotify
            self.launch_spotify()

            # Wait for 5 seconds to give the device time to register
            time.sleep(7)

            # Get a list of available devices
            devices = self.sp.devices()

            # If there are no devices available, return an error message
            if not devices['devices']:
                return "No devices found."

            # Get the ID of the first available device
            device_id = devices['devices'][0]['id']

            # Transfer playback to the device
            self.sp.transfer_playback(device_id=device_id)

            # Get the current playback status
            current_playback = self.sp.current_playback()

            # If there is currently a song playing, continue playing it
            if current_playback and current_playback['is_playing']:
                return "Continuing to play current song"

            # Otherwise, search for the song and play it
            results = self.sp.search(q=song_name, limit=1)
            if results['tracks']['items']:
                song_uri = results['tracks']['items'][0]['uri']
                self.sp.start_playback(uris=[song_uri])
                return f"Now playing {song_name}"
            else:
                return "Song not found."
        except spotipy.exceptions.SpotifyException as e:
            return f"An error occurred: {e}"
import os
import json
from datetime import datetime

class CommandProcessor:
    def __init__(self, jaicat):
        """
        Initialize the CommandProcessor.
        Args:
            jaicat (object): Reference to the main Jaicat assistant.
        """
        self.jaicat = jaicat
        self.commands = {}  # Dictionary to store dynamically added commands

        # Initialize pre-defined commands
        self.register_default_commands()

    def register_default_commands(self):
        """
        Register a set of default commands.
        """
        self.add_command("hello", self.say_hello)
        self.add_command("time", self.get_time)
        self.add_command("date", self.get_date)
        self.add_command("weather", self.get_weather)
        self.add_command("calendar", self.get_calendar)
        self.add_command("play music", self.play_music)

    def add_command(self, command_name, handler):
        """
        Add a new command dynamically.
        Args:
            command_name (str): The command's trigger keyword.
            handler (function): The function to execute when the command is triggered.
        """
        self.commands[command_name] = handler

    def execute_command(self, command_name, *args, **kwargs):
        """
        Execute a command by its name.
        Args:
            command_name (str): Name of the command to execute.
        Returns:
            Any: The result of the command's handler function.
        """
        command = self.commands.get(command_name)
        if command:
            return command(*args, **kwargs)
        else:
            return f"Command '{command_name}' not found."

    def say_hello(self):
        return "Hello, how can I assist you today?"

    def get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def get_date(self):
        return datetime.now().strftime("%Y-%m-%d")

    def get_weather(self):
        return self.jaicat.weather_service.get_weather()

    def get_calendar(self):
        return self.jaicat.calendar_service.get_upcoming_events()

    def play_music(self, song_title=None):
        if song_title:
            return self.jaicat.spotify_service.play_song(song_title)
        else:
            return "No song title provided."

    def process_user_input(self, user_input):
        """
        Process the user's input and execute corresponding commands.
        Args:
            user_input (str): The user's command.
        Returns:
            str: The result or response of the executed command.
        """
        user_input = user_input.lower()
        for command_name in self.commands:
            if command_name in user_input:
                return self.execute_command(command_name, user_input)
        return "Sorry, I didn't understand that command."

@echo off
setlocal enabledelayedexpansion

REM Set working paths
set "BASEDIR=%~dp0"
set "COMMANDDIR=%BASEDIR%command"
set "APPDIR=%BASEDIR%app"

REM --- Create files ---

echo Creating command\registry.py...
> "%COMMANDDIR%\registry.py" (
echo _REGISTRY = {}
echo.
echo def command(name):
echo.    def wrap(fn):
echo.        _REGISTRY[name] = fn
echo.        return fn
echo.    return wrap
echo.
echo def get_registry():
echo.    return dict(_REGISTRY)
)

echo Creating command\builtin.py...
> "%COMMANDDIR%\builtin.py" (
echo from Core.command_router import CommandRouter
echo from Core.service_container import ServiceContainer
echo.
echo def register_builtin_commands(router: CommandRouter, services: ServiceContainer):
echo.    spotify = services.resolve("spotify")
echo.    weather = services.resolve("weather")
echo.    calendar = services.resolve("calendar")
echo.
echo.    def play_music(_entities):
echo.        try:
echo.            return spotify.play_song("Imagine")
echo.        except Exception as e:
echo.            return f"Couldn't play music: {e}"
echo.
echo.    def request_weather(_entities):
echo.        try:
echo.            return weather.get_weather()
echo.        except Exception as e:
echo.            return f"Weather error: {e}"
echo.
echo.    def request_calendar(_entities):
echo.        try:
echo.            return calendar.get_current_date()
echo.        except Exception as e:
echo.            return f"Calendar error: {e}"
echo.
echo.    router.register("play_music", play_music)
echo.    router.register("request_weather", request_weather)
echo.    router.register("request_calendar", request_calendar)
)

echo Creating command\handler_table.py...
> "%COMMANDDIR%\handler_table.py" (
echo class CommandRegistry:
echo.    def __init__(self, **deps):
echo.        self.deps = deps
echo.        self._handlers = {
echo.            "play_music": self._play_music,
echo.            "turn_on_lights": self._turn_on_lights,
echo.            "generate_code": self._generate_code,
echo.            "analyze_text": self._analyze_text,
echo.            "analyze_sentiment": self._analyze_sentiment,
echo.        }
echo.
echo.    def can_handle(self, intent: str) -> bool:
echo.        return intent in self._handlers
echo.
echo.    def handle(self, intent, entities, raw_text, ctx):
echo.        return self._handlers[intent](entities, raw_text, ctx)
echo.
echo.    def _play_music(self, entities, raw_text, ctx):
echo.        return self.deps["spotify"].play_song("Imagine")
echo.
echo.    def _turn_on_lights(self, entities, raw_text, ctx):
echo.        return "Lights on!"
echo.
echo.    def _generate_code(self, entities, raw_text, ctx):
echo.        return "Code generation is wired—add your model call here."
echo.
echo.    def _analyze_text(self, entities, raw_text, ctx):
echo.        return str(ctx.nlp.analyze_text(raw_text))
echo.
echo.    def _analyze_sentiment(self, entities, raw_text, ctx):
echo.        return ctx.nlp.sentiment_analysis_model.analyze_sentiment(raw_text)
)

echo Creating command\processor.py...
> "%COMMANDDIR%\processor.py" (
echo from datetime import datetime
echo.
echo class CommandProcessor:
echo.    def __init__(self, jaicat):
echo.        self.jaicat = jaicat
echo.        self.commands = {}
echo.        self.register_default_commands()
echo.
echo.    def register_default_commands(self):
echo.        self.add_command("hello", self.say_hello)
echo.        self.add_command("time", self.get_time)
echo.        self.add_command("date", self.get_date)
echo.        self.add_command("weather", self.get_weather)
echo.        self.add_command("calendar", self.get_calendar)
echo.        self.add_command("play music", self.play_music)
echo.
echo.    def add_command(self, command_name, handler):
echo.        self.commands[command_name] = handler
echo.
echo.    def execute_command(self, command_name, *args, **kwargs):
echo.        fn = self.commands.get(command_name)
echo.        return fn(*args, **kwargs) if fn else f"Command '%s' not found." %% command_name
echo.
echo.    def process_user_input(self, user_input):
echo.        text = user_input.lower()
echo.        for name in self.commands:
echo.            if name in text:
echo.                return self.execute_command(name, user_input)
echo.        return "Sorry, I didn't understand that command."
echo.
echo.    def say_hello(self): return "Hello, how can I assist you today?"
echo.    def get_time(self):  return datetime.now().strftime("%%H:%%M:%%S")
echo.    def get_date(self):  return datetime.now().strftime("%%Y-%%m-%%d")
echo.    def get_weather(self):  return self.jaicat.weather_service.get_weather()
echo.    def get_calendar(self): return self.jaicat.calendar_service.get_upcoming_events()
echo.    def play_music(self, song_title=None):
echo.        return self.jaicat.spotify_service.play_song(song_title) if song_title else "No song title provided."
)

echo Creating app\bootstrap.py...
> "%APPDIR%\bootstrap.py" (
echo from Core.service_container import ServiceContainer
echo from Core.command_router import CommandRouter
echo.
echo from conversation.nlu import NLU
echo from features.nlp import NLPSystem
echo from conversation.nlg import ContextualResponder as NLG
echo from services.spotify_integration import SpotifyIntegration
echo from services.weather_service import WeatherService
echo from services.calendar_service import CalendarService
echo.
echo def build_services() -> ServiceContainer:
echo.    services = ServiceContainer()
echo.    services.register_singleton("nlu", NLU())
echo.    services.register_singleton("nlp", NLPSystem())
echo.    services.register_singleton("nlg", NLG())
echo.    services.register_singleton("spotify", SpotifyIntegration())
echo.    services.register_singleton("weather", WeatherService())
echo.    services.register_singleton("calendar", CalendarService())
echo.    return services
echo.
echo def build_controller():
echo.    services = build_services()
echo.    router = CommandRouter()
echo.
echo.    from command.builtin import register_builtin_commands
echo.    register_builtin_commands(router, services)
echo.
echo.    return router, services
)

echo All command + app files created.
pause

# Core/app.py

from __future__ import annotations

import pyttsx3
from dataclasses import dataclass
from typing import Tuple

# --- Core infra
from Core.service_container import ServiceContainer
from Core.command_router import CommandRouter
from Core.events import EventBus
from Core.registry import Registry
from Core.assets import Assets

# --- Models / conversation
from conversation.nlu import NLU
from features.nlp import NLPSystem
from conversation.nlg import ContextualResponder as NLG
from conversation.dialogue_manager import DialogueManager

# --- External services
from services.spotify_integration import SpotifyIntegration
from services.weather_service import WeatherService
from services.calendar_service import CalendarService

# --- Voice / Wake
from utils.speech import Speech
from services.wake_word import WakeWordListener

# --- GUI
from ui.JaicatUI import JaicatUI


# --- App initialization
# This function sets up the core services and returns them for use in the app.
# It also initializes the command router and registers built-in commands.
# This is the main entry point for the Jaicat application.
from command.builtin import register_builtin_commands







def build_app():
    services = ServiceContainer()
    events = EventBus()
    services.register_singleton("events", events)

    services.register_singleton("nlu", NLU())
    services.register_singleton("nlp", NLPSystem())
    services.register_singleton("nlg", NLG())

    services.register_singleton("spotify", SpotifyIntegration())
    services.register_singleton("weather", WeatherService())
    services.register_singleton("calendar", CalendarService())

    tts = Speech()
    services.register_singleton("speech", tts)

    router = CommandRouter()
    from command.builtin import register_builtin_commands
    register_builtin_commands(router, services)

    return services, router


@dataclass
class JaicatApp:
    nlp: NLPSystem
    nlu: NLU
    nlg: NLG
    music: SpotifyIntegration
    weather: WeatherService
    calendar: CalendarService
    speech: Speech
    assets: Assets
    events: EventBus
    registry: Registry

    @staticmethod
    def bootstrap() -> "JaicatApp":
        events = EventBus()
        registry = Registry(events)
        nlp = NLPSystem()
        nlu = NLU()
        nlg = NLG()
        weather = WeatherService()
        calendar = CalendarService()
        music = SpotifyIntegration()
        speech = Speech()
        assets = Assets()

        return JaicatApp(
            nlp=nlp, nlu=nlu, nlg=nlg,
            music=music, weather=weather, calendar=calendar,
            speech=speech, assets=assets, events=events, registry=registry
        )

    def handle_text(self, text: str) -> Tuple[str, str | None]:
        extracted = self.nlu.extract_intent_and_entities(text)
        intent = extracted.get("intent")
        entities = extracted.get("entities")
        sentiment = self.nlp.analyze_sentiment(text)
        mood = {"positive": "happy", "negative": "sad"}.get(sentiment, "neutral")
        self.events.publish("mood.changed", mood=mood)
        reply = self._route_intent(intent, entities, text)
        return reply, mood

    def _route_intent(self, intent: str | None, entities, raw_text: str) -> str:
        if intent in (None, "unknown"):
            return self.nlg.respond({}, raw_text)
        if intent == "play_music":
            self.music.play_song("Imagine")
            return "Playing your track."
        if intent == "request_weather":
            self.refresh_weather()
            return "Fetched the latest weather."
        if intent == "get_calendar":
            self.refresh_calendar()
            return "Here is your calendar."
        return self.nlg.respond({"intent": intent, "entities": entities}, raw_text)

    def refresh_weather(self):
        summary = self.weather.get_weather()
        self.events.publish("weather.updated", summary=summary)

    def refresh_calendar(self):
        today = self.calendar.get_current_date()
        self.events.publish("calendar.updated", today=today)

    def mood_phrase(self, mood: str) -> str:
        return {
            "happy": "I'm feeling great today!",
            "flirty": "Hello there, looking good!",
            "sad": "I'm feeling a bit down today."
        }.get(mood, "I'm here to assist you.")


class _RouterAdapter:
    def __init__(self, router: CommandRouter):
        self.router = router

    def can_handle(self, intent: str) -> bool:
        return self.router.can_handle(intent)

    def handle(self, intent, entities, text, ctx=None):
        return self.router.handle(intent, entities, text, ctx=ctx)
    



def run_ui():
    services, router = build_app()
    nlp = services.resolve("nlp")
    nlu = services.resolve("nlu")
    nlg = services.resolve("nlg")
    spotify = services.resolve("spotify")
    weather = services.resolve("weather")
    calendar = services.resolve("calendar")
    speech = services.resolve("speech")
    assets = services.resolve("assets")
    events = services.resolve("events")
    registry = services.resolve("registry")
    # Initialize the app with all services
    app = JaicatApp(
        nlp=nlp, nlu=nlu, nlg=nlg,
        music=spotify, weather=weather, calendar=calendar,
        speech=speech, assets=assets, events=events, registry=registry
    )
    # Register built-in commands
    register_builtin_commands(router, services)
    # Initialize the dialogue manager with NLU and NLP
    # and pass the command router as the tool registry
    nlg.contextual_responder = nlg  # Use NLG as the responder
    dialogue = DialogueManager(nlu=nlu, nlp_system=nlp, contextual_responder=nlg, tool_registry=_RouterAdapter(router))  # Pass the command router  as tool_registry
    # Initialize the controller with all components
    # and set the active user tenant to "Jay" if not already set
    if not app.current_user:
        app.current_user = "Jay"
    if app.active_user_tenant in (None, "", "public"):
        app.active_user_tenant = "Jay"
    if hasattr(dialogue, "context"):
        dialogue.context["tenant"] = app.active_user_tenant

    from app.controller import JaicatController
    dm = DialogueManager(nlu=nlu, nlp_system=nlp)
    commands = _RouterAdapter(router)
    controller = JaicatController(nlp, nlu, dm, spotify, weather, calendar, commands, tts=speech)

    if not controller.current_user:
        controller.current_user = "Jay"
    if controller.active_user_tenant in (None, "", "public"):
        controller.active_user_tenant = "Jay"
    if hasattr(dm, "context"):
        dm.context["tenant"] = controller.active_user_tenant

        # Core/app.py  (inside run_ui())
    ui = JaicatUI(controller=controller)
    controller.set_ui(ui)

    # If the UI exposes a tools registry, wire it into DialogueManager:
    if hasattr(ui, "tools"):
        try:
            dm.tool_registry = ui.tools  # <-- hand tools to DM
        except Exception:
            pass

    # Wake word stays as-is
    wake = WakeWordListener(on_wake=controller.on_wake, device_index=None)
    wake.start()
    ui.mainloop()
    wake.stop()

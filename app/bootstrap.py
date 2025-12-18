# app/bootstrap.py
from Core.service_container import ServiceContainer
from Core.command_router import CommandRouter
from app.controller import Controller

# ---- Core brains ----
from conversation.nlu import NLU
from conversation.nlg import ContextualResponder as NLG
from conversation.dialogue_manager import DialogueManager
from features.nlp import NLPSystem

# ---- Integrations ----
from services.spotify_integration import SpotifyIntegration
from services.weather_service import WeatherService
from services.calendar_service import CalendarService
from services.email_service import EmailService
from services.email_classifier import EmailClassifier
from services.email_service import EmailService

# ---- Models (guarded) ----
try:
    from models.text_classification_model import TextClassifier  # optional
except Exception:
    TextClassifier = None

# ---- Voice ----
from utils.speech import Speech
from services.wake_word import WakeWordListener  # add with other imports
# ---- Command registrations ----
import command.builtin as builtin


def build_services() -> ServiceContainer:
    """Register everything once; avoid duplicate singletons."""
    svc = ServiceContainer()
    svc.register_singleton("email", EmailService())
    svc.register_singleton("wake_word", WakeWordListener())
    # Core intelligence
    svc.register_singleton("nlu", NLU())
    svc.register_singleton("nlg", NLG())
    svc.register_singleton("nlp", NLPSystem())
    svc.register_singleton("dialogue_manager", DialogueManager())

    # Voice
    svc.register_singleton("speech", Speech())

    # Integrations (choose one per domain)
    svc.register_singleton("spotify", SpotifyIntegration())
    svc.register_singleton("weather", WeatherService())
    svc.register_singleton("calendar", CalendarService())

    # Email stack (no duplicate registration)
    svc.register_singleton("email", EmailService())
    if TextClassifier is not None:
        svc.register_singleton(
            "email_classifier",
            EmailClassifier(nlp=svc.resolve("nlp"), classifier_model=TextClassifier())
        )

    # Optional smart_home:
    # from services.smart_home import SmartHome
    # svc.register_singleton("smart_home", SmartHome())

    return svc


def _attach_ui_helpers(controller: Controller) -> None:
    """
    Add small helpers the UI expects (learn from link/file) without hard-coding imports there.
    These are no-ops if kb.ingest isn't available.
    """
    # learn from file
    def ingest_file(path: str) -> str:
        try:
            from kb.ingest import ingest_file as _ingest_file
        except Exception:
            return "Ingest module not available."
        try:
            _ingest_file(path)
            return "Learned from file."
        except Exception as e:
            return f"Ingest error: {e}"

    # learn from link
    def ingest_url(url: str) -> str:
        try:
            from kb.ingest import ingest_url as _ingest_url
        except Exception:
            return "Ingest module not available."
        try:
            _ingest_url(url)
            return "Learned from link."
        except Exception as e:
            return f"Ingest error: {e}"

    # attach
    controller.ingest_file = ingest_file
    controller.ingest_url = ingest_url


def build_controller() -> Controller:
    """
    Build the DI container, the router, register built-in commands, and return a ready controller.
    """
    services = build_services()
    router = CommandRouter()

    # Single source of commands
    if hasattr(builtin, "register_all"):
        builtin.register_all(router, services)

    controller = Controller(services, router)
    _attach_ui_helpers(controller)
    return controller

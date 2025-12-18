# Core/command_router.py
from __future__ import annotations
from typing import Callable, Dict, Any

Handler = Callable[..., Any]

class CommandRouter:
    """
    Minimal intent→handler router.

    API:
      - register(intent: str, fn: Callable)
      - can_handle(intent: str) -> bool
      - handle(intent: str, *args, **kwargs) -> Any
      - intents() -> list[str]
    """
    def __init__(self) -> None:
        self._handlers: Dict[str, Handler] = {}

    def register(self, intent: str, fn: Handler) -> None:
        if not intent or not callable(fn):
            raise ValueError("register() requires an intent string and a callable")
        self._handlers[intent] = fn

    def can_handle(self, intent: str) -> bool:
        return bool(intent) and intent in self._handlers

    def handle(self, intent: str, *args, **kwargs) -> Any:
        if not self.can_handle(intent):
            raise KeyError(f"No handler registered for intent: {intent!r}")
        return self._handlers[intent](*args, **kwargs)

    def intents(self):
        return list(self._handlers.keys())

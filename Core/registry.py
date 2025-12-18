# core/registry.py
from __future__ import annotations
import importlib
import pkgutil
from typing import Callable
from Core.events import EventBus
from typing import Callable, Dict, Any

class Tool:
    def __init__(self, name: str, handler: Callable[[dict], str], intents: list[str]):
        self.name = name
        self.handler = handler
        self.intents = intents

class ToolRegistry:
    def __init__(self):
        self._by_intent: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        for intent in tool.intents:
            self._by_intent[intent] = tool

    def dispatch(self, intent: str, entities: dict) -> str:
        tool = self._by_intent.get(intent)
        if not tool:
            return "I don't have a tool for that yet."
        return tool.handler(entities)

class Registry:
    def __init__(self, events: EventBus):
        self.events = events
        self.hooks: dict[str, list[Callable]] = {}

    def hook(self, name: str, fn: Callable):
        self.hooks.setdefault(name, []).append(fn)

    def call(self, name: str, *args, **kwargs):
        for fn in self.hooks.get(name, []):
            fn(*args, **kwargs)

    def autodiscover(self, package: str):
        try:
            pkg = importlib.import_module(package)
        except ImportError:
            return
        for m in pkgutil.iter_modules(pkg.__path__, pkg.__name__ + "."):
            importlib.import_module(m.name)

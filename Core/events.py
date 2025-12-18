# core/events.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List
# core/events.py
from collections import defaultdict
from typing import Callable

class EventBus:
    def __init__(self):
        self._subs = defaultdict(list)

    def subscribe(self, topic: str, fn: Callable):
        self._subs[topic].append(fn)

    def publish(self, topic: str, payload=None):
        for fn in self._subs.get(topic, []):
            fn(payload)

@dataclass
class Event:
    type: str
    payload: Dict[str, Any]

class EventBus:
    def __init__(self):
        self._subs: List[Callable[[Event], None]] = []

    def subscribe(self, cb: Callable[[Event], None]):
        self._subs.append(cb)

    def publish(self, type_: str, **payload):
        ev = Event(type_, payload)
        for cb in list(self._subs):
            cb(ev)

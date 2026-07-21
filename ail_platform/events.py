from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class Event:
    type: str
    data: dict = field(default_factory=dict)


EventHandler = Callable[["Event"], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def on(self, event_type: str, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def emit(self, event: Event) -> None:
        for handler in self._handlers[event.type]:
            handler(event)

    def clear(self) -> None:
        self._handlers.clear()

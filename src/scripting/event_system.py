"""
Event system for Lua script runtime.

Manages event registration, dispatching, and trigger pattern matching.
Bridges between MUD input (text, GMCP) and Lua event handlers.
"""

import logging
import re
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Built-in event types."""
    ON_MESSAGE = "on_message"           # MUD text received
    ON_GMCP = "on_gmcp"                 # GMCP module received
    ON_VITALS = "on_vitals"             # HP/MP changed
    ON_ROOM = "on_room"                 # Room entered
    ON_MOVEMENT = "on_movement"         # Direction moved
    ON_COMBAT = "on_combat"             # Combat event
    ON_TRIGGER = "on_trigger"           # Custom trigger matched
    ON_ALIAS = "on_alias"               # Alias executed
    ON_TIMER = "on_timer"               # Timer fired


@dataclass
class Event:
    """Event data."""
    type: EventType
    data: Dict[str, Any]
    source: str = "system"


class EventHandler:
    """Registered event handler with pattern matching."""

    def __init__(self, event_type: EventType, handler: Callable,
                 pattern: Optional[str] = None, flags: int = 0):
        """
        Initialize handler.

        Args:
            event_type: Event type to handle
            handler: Callback function
            pattern: Optional regex pattern for matching
            flags: Regex flags (re.IGNORECASE, etc.)
        """
        self.event_type = event_type
        self.handler = handler
        self.pattern = pattern
        self.regex = None
        self.flags = flags

        if pattern:
            try:
                self.regex = re.compile(pattern, flags)
            except re.error as e:
                logger.error(f"Invalid regex pattern '{pattern}': {e}")

    def matches(self, text: str) -> bool:
        """Check if event text matches handler pattern."""
        if not self.regex:
            return True
        return bool(self.regex.search(text))

    def extract_captures(self, text: str) -> List[str]:
        """Extract capture groups from text."""
        if not self.regex:
            return []
        match = self.regex.search(text)
        if match:
            return list(match.groups())
        return []


class EventSystem:
    """Manages event registration and dispatching."""

    def __init__(self):
        """Initialize event system."""
        self.handlers: Dict[EventType, List[EventHandler]] = {
            event_type: [] for event_type in EventType
        }
        self.event_queue: List[Event] = []
        self.enabled = True

    def register_handler(self, event_type: EventType, handler: Callable,
                        pattern: Optional[str] = None,
                        case_insensitive: bool = True):
        """
        Register event handler.

        Args:
            event_type: Event type to listen for
            handler: Callback function(event_data, captures)
            pattern: Optional regex pattern to match
            case_insensitive: If True, ignore case in pattern matching
        """
        flags = re.IGNORECASE if case_insensitive else 0
        event_handler = EventHandler(event_type, handler, pattern, flags)
        self.handlers[event_type].append(event_handler)

        logger.debug(f"Registered handler for {event_type.value}")

    def emit(self, event_type: EventType, data: Dict[str, Any]):
        """
        Emit event to all registered handlers.

        Args:
            event_type: Type of event
            data: Event data dictionary
        """
        if not self.enabled:
            return

        event = Event(event_type, data)
        self.event_queue.append(event)
        self._process_event(event)

    def _process_event(self, event: Event):
        """Process single event against all handlers."""
        handlers = self.handlers.get(event.type, [])

        # Find text to match against (varies by event type)
        text_to_match = ""
        if event.type == EventType.ON_MESSAGE:
            text_to_match = event.data.get('text', '')
        elif event.type == EventType.ON_TRIGGER:
            text_to_match = event.data.get('pattern', '')

        for handler in handlers:
            try:
                # Check if handler pattern matches
                if not handler.matches(text_to_match):
                    continue

                # Extract capture groups
                captures = handler.extract_captures(text_to_match)

                # Call handler
                if captures:
                    handler.handler(event.data, captures)
                else:
                    handler.handler(event.data)

                logger.debug(f"Handler executed for {event.type.value}")

            except Exception as e:
                logger.error(f"Error in event handler: {e}", exc_info=True)

    def on_mud_message(self, channel: str, text: str):
        """Handle MUD text message (from telnet/connection)."""
        self.emit(EventType.ON_MESSAGE, {
            'channel': channel,
            'text': text,
        })

    def on_gmcp_module(self, module: str, data: Dict[str, Any]):
        """Handle GMCP module data."""
        self.emit(EventType.ON_GMCP, {
            'module': module,
            'data': data,
        })

    def on_vitals_changed(self, hp: int, maxhp: int, mp: int, maxmp: int):
        """Handle character vitals change (HP/MP)."""
        self.emit(EventType.ON_VITALS, {
            'hp': hp,
            'maxhp': maxhp,
            'mp': mp,
            'maxmp': maxmp,
        })

    def on_room_entered(self, room_name: str, exits: List[str]):
        """Handle room entry."""
        self.emit(EventType.ON_ROOM, {
            'room': room_name,
            'exits': exits,
        })

    def on_movement(self, direction: str):
        """Handle movement command."""
        self.emit(EventType.ON_MOVEMENT, {
            'direction': direction,
        })

    def on_combat_event(self, event_type: str, **kwargs):
        """Handle combat-related event."""
        self.emit(EventType.ON_COMBAT, {
            'event': event_type,
            **kwargs
        })

    def clear(self):
        """Clear all registered handlers."""
        for event_type in self.handlers:
            self.handlers[event_type].clear()
        logger.debug("Event system cleared")

    def disable(self):
        """Disable event processing."""
        self.enabled = False
        logger.info("Event system disabled")

    def enable(self):
        """Enable event processing."""
        self.enabled = True
        logger.info("Event system enabled")

    def get_statistics(self) -> Dict[str, Any]:
        """Get event system statistics."""
        return {
            'total_handlers': sum(len(h) for h in self.handlers.values()),
            'handlers_by_type': {
                et.value: len(h) for et, h in self.handlers.items()
            },
            'queued_events': len(self.event_queue),
            'enabled': self.enabled,
        }

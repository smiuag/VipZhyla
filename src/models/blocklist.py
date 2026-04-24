"""
BlockList system for VipZhyla - Filter messages by player, keyword, or channel.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set


@dataclass
class BlockList:
    """Manages blocked players, keywords, and channels."""

    blocked_players: Set[str] = field(default_factory=set)
    blocked_keywords: Set[str] = field(default_factory=set)
    blocked_channels: Set[str] = field(default_factory=set)

    SAVE_PATH = Path("src/data/blocklist.json")

    def should_filter(self, text: str, channel: str = "") -> bool:
        """Check if message should be filtered from display.

        Args:
            text: Message text
            channel: Channel name (e.g., "bando", "telepathy")

        Returns:
            True if message should be filtered (hidden), False otherwise
        """
        text_lower = text.lower()

        # Check blocked channels
        if channel and channel.lower() in self.blocked_channels:
            return True

        # Check blocked keywords
        for keyword in self.blocked_keywords:
            if keyword.lower() in text_lower:
                return True

        # Check blocked players (pattern: "Name dice:", "Name grita:", etc.)
        player_pattern = r'^(\w+)\s+(?:dice|grita|susurra|canta|cuenta|pregunta|avisa):'
        match = re.match(player_pattern, text, re.IGNORECASE)
        if match:
            player_name = match.group(1)
            if player_name.lower() in self.blocked_players:
                return True

        return False

    def add_player(self, name: str) -> None:
        """Add a player to blocklist."""
        if name and name.strip():
            self.blocked_players.add(name.strip().lower())
            self.save()

    def remove_player(self, name: str) -> None:
        """Remove a player from blocklist."""
        self.blocked_players.discard(name.lower())
        self.save()

    def add_keyword(self, keyword: str) -> None:
        """Add a keyword to blocklist."""
        if keyword and keyword.strip():
            self.blocked_keywords.add(keyword.strip().lower())
            self.save()

    def remove_keyword(self, keyword: str) -> None:
        """Remove a keyword from blocklist."""
        self.blocked_keywords.discard(keyword.lower())
        self.save()

    def add_channel(self, channel: str) -> None:
        """Add a channel to blocklist."""
        if channel and channel.strip():
            self.blocked_channels.add(channel.strip().lower())
            self.save()

    def remove_channel(self, channel: str) -> None:
        """Remove a channel from blocklist."""
        self.blocked_channels.discard(channel.lower())
        self.save()

    def clear_all(self) -> None:
        """Clear all blocks."""
        self.blocked_players.clear()
        self.blocked_keywords.clear()
        self.blocked_channels.clear()
        self.save()

    def get_stats(self) -> dict:
        """Get blocking statistics."""
        return {
            'players': len(self.blocked_players),
            'keywords': len(self.blocked_keywords),
            'channels': len(self.blocked_channels),
            'total': len(self.blocked_players) + len(self.blocked_keywords) + len(self.blocked_channels),
        }

    def save(self) -> None:
        """Save blocklist to JSON."""
        self.SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'blocked_players': sorted(list(self.blocked_players)),
            'blocked_keywords': sorted(list(self.blocked_keywords)),
            'blocked_channels': sorted(list(self.blocked_channels)),
        }

        with open(self.SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self) -> None:
        """Load blocklist from JSON."""
        if not self.SAVE_PATH.exists():
            return

        try:
            with open(self.SAVE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.blocked_players = set(data.get('blocked_players', []))
            self.blocked_keywords = set(data.get('blocked_keywords', []))
            self.blocked_channels = set(data.get('blocked_channels', []))

        except (json.JSONDecodeError, IOError):
            pass  # File corrupted or unreadable; use empty blocklist

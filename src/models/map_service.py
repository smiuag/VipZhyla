"""
Map and navigation service for VipZhyla.

Tracks player position, resolves room names to IDs, performs pathfinding,
and supports room searching.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from collections import deque
from typing import Optional


@dataclass
class MapRoom:
    """A room in the MUD."""
    id: int
    n: str  # short name
    x: int
    y: int
    z: int
    e: dict[str, int]  # exits: {key → room_id}
    fn: Optional[str] = None  # full name with bracket


class MapService:
    """Manage map data, current position, and navigation."""

    # Direction normalization: MUD words → short keys
    CMD_TO_KEY = {
        'norte': 'n',
        'sur': 's',
        'este': 'e',
        'oeste': 'o',
        'noreste': 'ne',
        'noroeste': 'no',
        'sureste': 'se',
        'suroeste': 'so',
        'arriba': 'ar',
        'abajo': 'ab',
        'dentro': 'de',
        'fuera': 'fu',
    }

    # Reverse mapping: short keys → MUD words
    KEY_TO_CMD = {v: k for k, v in CMD_TO_KEY.items()}

    def __init__(self):
        """Initialize map service."""
        self.rooms: dict[int, MapRoom] = {}
        self.name_index: dict[str, list[int]] = {}
        self.current_room_id: Optional[int] = None

    def load(self, json_path: str | Path) -> bool:
        """Load map from JSON file.

        Args:
            json_path: Path to map-reinos.json

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Clear existing data
            self.rooms = {}
            self.name_index = {}
            self.current_room_id = None

            # Load rooms
            for room_id_str, room_data in data.get('rooms', {}).items():
                room_id = int(room_id_str)
                self.rooms[room_id] = MapRoom(
                    id=room_id,
                    n=room_data.get('n', 'Unknown'),
                    x=int(room_data.get('x', 0)),
                    y=int(room_data.get('y', 0)),
                    z=int(room_data.get('z', 0)),
                    e={k: int(v) for k, v in room_data.get('e', {}).items()},
                    fn=room_data.get('fn'),
                )

            # Load name index (case-fold for lookup)
            for name, room_ids in data.get('nameIndex', {}).items():
                # Store both original and lowercase for matching
                self.name_index[name.lower()] = [int(id) for id in room_ids]

            return True
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return False

    def set_current_room(self, room_id: int) -> None:
        """Set current player room."""
        if room_id in self.rooms:
            self.current_room_id = room_id

    def get_current_room(self) -> Optional[MapRoom]:
        """Get current room or None if not localized."""
        if self.current_room_id is None:
            return None
        return self.rooms.get(self.current_room_id)

    def find_room(self, line: str) -> Optional[MapRoom]:
        """Find room from a line like 'Name [exits]'.

        Args:
            line: Room line with name and exits bracket

        Returns:
            MapRoom if found, None if ambiguous or not found
        """
        # Strip prompt characters
        line = line.lstrip('> ]').strip()

        # Parse 'Name [exits]'
        match = re.match(r'^(.*?)\s*\[(.*?)\]\s*$', line)
        if not match:
            return None

        short_name = match.group(1).strip()
        exits_str = match.group(2).strip()

        # Normalize exits to keys
        exit_parts = [e.strip().lower() for e in exits_str.split(',')]
        expected_exits = set(self.CMD_TO_KEY.get(e, e) for e in exit_parts)

        # Look up in name index (case-insensitive)
        candidates = self.name_index.get(short_name.lower(), [])

        if not candidates:
            return None

        # If 1 candidate, return it
        if len(candidates) == 1:
            return self.rooms.get(candidates[0])

        # Multiple candidates: filter by exact exit set match
        for room_id in candidates:
            room = self.rooms.get(room_id)
            if room and set(room.e.keys()) == expected_exits:
                return room

        # Still ambiguous after exit filtering
        return None

    def move_by_direction(self, direction: str) -> Optional[MapRoom]:
        """Move in a direction from current room.

        Args:
            direction: MUD word (norte, sur, etc.) or short key

        Returns:
            New MapRoom if move successful, None if can't move or not localized
        """
        if self.current_room_id is None:
            return None

        current = self.rooms.get(self.current_room_id)
        if not current:
            return None

        # Normalize direction to key
        key = self.CMD_TO_KEY.get(direction.lower(), direction.lower())

        # Look up exit
        next_room_id = current.e.get(key)
        if next_room_id is None:
            return None

        # Update position
        self.current_room_id = next_room_id
        return self.rooms.get(next_room_id)

    def search_rooms(self, query: str) -> list[MapRoom]:
        """Search for rooms by partial name.

        Args:
            query: Partial room name (case-insensitive)

        Returns:
            List of matching rooms (max 20)
        """
        query_lower = query.lower()
        results = []

        for room in self.rooms.values():
            if query_lower in room.n.lower():
                results.append(room)
                if len(results) >= 20:
                    break

        return results

    def find_path(self, from_id: int, to_id: int) -> Optional[list[str]]:
        """Find path between two rooms using BFS.

        Args:
            from_id: Starting room ID
            to_id: Destination room ID

        Returns:
            List of MUD commands (e.g., ['norte', 'este']) or None if unreachable
        """
        if from_id not in self.rooms or to_id not in self.rooms:
            return None

        if from_id == to_id:
            return []

        # BFS
        queue = deque([(from_id, [])])
        visited = {from_id}
        max_visited = 50000

        while queue and len(visited) < max_visited:
            room_id, path = queue.popleft()
            room = self.rooms[room_id]

            for key, next_id in room.e.items():
                if next_id == to_id:
                    # Found destination
                    cmd = self.KEY_TO_CMD.get(key, key)
                    return path + [cmd]

                if next_id not in visited:
                    visited.add(next_id)
                    cmd = self.KEY_TO_CMD.get(key, key)
                    queue.append((next_id, path + [cmd]))

        return None  # Unreachable or max nodes exceeded

"""
Character state parser — extracts character info from GMCP and MUD output.

Sources of character data:
1. GMCP Char.Status (class, race, level, name)
2. GMCP Char.Vitals (HP, MP)
3. MUD console output (patterns for class/race when GMCP unavailable)
"""

import re
from typing import Optional, Dict, Any
from models.character_state import CharacterState


class CharacterParser:
    """Parse character data from GMCP and MUD output."""

    # VipMud classes from scripts.md
    KNOWN_CLASSES = {
        'soldado', 'druida', 'mago', 'paladín', 'cazador', 'pícaro',
        'bardo', 'monje', 'chamán', 'templario', 'nigromante', 'hechicero'
    }

    # Races from scripts.md (Reinos de Leyenda)
    KNOWN_RACES = {
        'elfo', 'enano', 'humano', 'gnomo', 'orco', 'drow',
        'medio-elfo', 'medio-orco', 'halfling', 'troll'
    }

    @staticmethod
    def parse_gmcp_status(state: CharacterState, data: Dict[str, Any]) -> None:
        """Update character state from GMCP Char.Status.

        Data format:
        {
            "name": "Aeroth",
            "level": 42,
            "class": "Soldado",
            "race": "Elfo",
            "experience": 50000
        }
        """
        if 'name' in data:
            state.name = str(data['name'])

        if 'level' in data:
            state.level = int(data.get('level', 0))

        if 'class' in data:
            clase = str(data['class']).lower()
            if clase in CharacterParser.KNOWN_CLASSES:
                state.clase = data['class']

        if 'race' in data:
            raza = str(data['race']).lower()
            if raza in CharacterParser.KNOWN_RACES:
                state.raza = data['race']

    @staticmethod
    def parse_gmcp_vitals(state: CharacterState, data: Dict[str, Any]) -> None:
        """Update character state from GMCP Char.Vitals.

        Data format:
        {
            "hp": 320,
            "maxhp": 450,
            "mp": 120,
            "maxmp": 200,
            "energy": 100 (optional)
        }
        """
        try:
            hp = int(data.get('hp', 0))
            maxhp = int(data.get('maxhp', 0))
            mp = int(data.get('mp', 0))
            maxmp = int(data.get('maxmp', 0))
            energy = int(data.get('energy', 0))

            state.update_vitals(hp, maxhp, mp, maxmp)

            if 'energy' in data:
                state.energy = energy
                if maxhp > 0:
                    state.energy_pct = int((energy / maxhp) * 100)

        except (ValueError, TypeError):
            pass

    @staticmethod
    def extract_class_from_console(text: str) -> Optional[str]:
        """Try to extract class from console output.

        Patterns like:
        - "You are a Soldado"
        - "Eres un Druida"
        - "Clase: Paladín"
        """
        patterns = [
            r'(?:You are|Eres|Soy)\s+(?:a|un|una)\s+(\w+)',
            r'(?:Class|Clase):\s*(\w+)',
            r'^\s*(\w+)$'  # Single word (last resort)
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                word = match.group(1).lower()
                if word in CharacterParser.KNOWN_CLASSES:
                    return word.capitalize()

        return None

    @staticmethod
    def extract_race_from_console(text: str) -> Optional[str]:
        """Try to extract race from console output.

        Patterns like:
        - "You are an Elfo"
        - "Eres un Enano"
        - "Raza: Humano"
        """
        patterns = [
            r'(?:You are|Eres|Soy)\s+(?:a|an|un|una)\s+(\w+)',
            r'(?:Race|Raza):\s*(\w+)',
            r'(?:race|raza)\s+of\s+(\w+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                word = match.group(1).lower()
                if word in CharacterParser.KNOWN_RACES:
                    return word.capitalize()

        return None

    @staticmethod
    def extract_hp_from_console(text: str) -> Optional[tuple[int, int]]:
        """Try to extract HP (current, max) from console output.

        Patterns like:
        - "HP: 320/450"
        - "Vida: 100 de 200"
        - "320 health / 450"
        """
        patterns = [
            r'HP:\s*(\d+)\s*[/\-de]\s*(\d+)',
            r'(?:Life|Health|Vida):\s*(\d+)\s*[/\-de]\s*(\d+)',
            r'(\d+)\s*(?:health|HP)\s*[/\-]\s*(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    hp = int(match.group(1))
                    maxhp = int(match.group(2))
                    return (hp, maxhp)
                except (ValueError, IndexError):
                    pass

        return None

"""
Character validation utilities.

NOTE: Game state parsing removed in Phase 7B cleanup.
Lua modules (game.character, game.estados, game.estadisticas) are the single source of truth.
This file provides only validation helpers for class/race names.
"""

from typing import Optional


class CharacterParser:
    """Utility for character data validation (game state parsing moved to Lua)."""

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
    def is_valid_class(clase: str) -> bool:
        """Validate if class name is recognized."""
        return clase.lower() in CharacterParser.KNOWN_CLASSES

    @staticmethod
    def is_valid_race(raza: str) -> bool:
        """Validate if race name is recognized."""
        return raza.lower() in CharacterParser.KNOWN_RACES

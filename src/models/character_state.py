from dataclasses import dataclass, field


@dataclass
class CharacterState:
    """UI display state for character information.

    NOTE: Game state (HP, buffs, inventory, etc.) is now managed by Lua modules.
    This class is only for local Python UI updates and spam prevention.

    Read from Lua via: script_loader.lua.globals()['game'].character
                       script_loader.lua.globals()['game'].estados
                       script_loader.lua.globals()['game'].estadisticas

    Phase 7B-bugfix: Restored slim character attributes (name/level/class/hp/etc.)
    so Python UI code (main.py, triggers.py) can read defaults without crashing
    when Lua hasn't populated state yet. Lua remains the source of truth — these
    fields are mirrors maintained by GMCP callbacks / update_from_lua().
    """

    # UI Display State (read-only, synced from Lua)
    hp_pct: int = 0                   # Porcentaje (0-100) — para triggers locales
    mp_pct: int = 0

    # Restored mirror fields (BUG #2 fix). Lua is still source of truth.
    name: str = "Unknown"
    level: int = 0
    character_class: str = ""
    clase: str = ""                   # Spanish alias used by triggers
    raza: str = ""
    hp: int = 0
    max_hp: int = 0
    maxhp: int = 0                    # Alias for max_hp (used in triggers)
    mp: int = 0
    max_mp: int = 0
    maxmp: int = 0                    # Alias for max_mp (used in triggers)
    in_combat: bool = False
    buffs: list = field(default_factory=list)
    debuffs: list = field(default_factory=list)
    room_name: str = ""
    room_exits: list = field(default_factory=list)
    room_description: str = ""

    # Spam Prevention Flags (Python-side trigger optimization only)
    # Maps threshold (100, 90, 60, 30, 10) to whether we've already announced it
    hp_threshold_flags: dict[int, bool] = field(
        default_factory=lambda: {100: False, 90: False, 60: False, 30: False, 10: False}
    )

    def should_announce_hp_threshold(self, threshold: int) -> bool:
        """Check if we should announce this HP threshold (Python trigger optimization only)."""
        if self.hp_threshold_flags.get(threshold, False):
            return False  # Already announced
        self.hp_threshold_flags[threshold] = True
        return True

    def reset_hp_thresholds(self):
        """Reset HP threshold flags when HP increases significantly."""
        for key in self.hp_threshold_flags:
            self.hp_threshold_flags[key] = False

    def get_hp_threshold(self) -> int | None:
        """Get the current HP threshold (100, 90, 60, 30, 10, or None)."""
        if self.hp_pct >= 90:
            return 100
        elif self.hp_pct >= 60:
            return 90
        elif self.hp_pct >= 30:
            return 60
        elif self.hp_pct >= 10:
            return 30
        elif self.hp_pct > 0:
            return 10
        return None

    def update_vitals(self, hp: int, max_hp: int, mp: int = 0, max_mp: int = 0) -> None:
        """Update HP/MP values and recompute percentages.

        Args:
            hp: Current HP
            max_hp: Maximum HP
            mp: Current MP (optional)
            max_mp: Maximum MP (optional)
        """
        self.hp = hp
        self.max_hp = max_hp
        self.maxhp = max_hp
        self.mp = mp
        self.max_mp = max_mp
        self.maxmp = max_mp
        self.hp_pct = int((hp / max_hp) * 100) if max_hp > 0 else 0
        self.mp_pct = int((mp / max_mp) * 100) if max_mp > 0 else 0

    def update_from_lua(self, lua_character: dict, lua_estados: dict) -> None:
        """Update UI display state from Lua game state.

        Args:
            lua_character: game.character from Lua
            lua_estados: game.estados.state from Lua
        """
        if lua_character and lua_character.get('maxhp', 0) > 0:
            self.hp_pct = int((lua_character.get('hp', 0) / lua_character['maxhp']) * 100)
        if lua_character and lua_character.get('maxmp', 0) > 0:
            self.mp_pct = int((lua_character.get('mp', 0) / lua_character['maxmp']) * 100)

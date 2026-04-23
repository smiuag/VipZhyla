from dataclasses import dataclass, field


@dataclass
class CharacterState:
    """Character state tracking for triggers and game mechanics.

    Based on VipMud's Estados.set pattern. All fields are used for trigger conditions,
    state tracking, and spam prevention (HP threshold flags).
    """

    # Identity
    name: str = ""                    # Nombre del PJ
    clase: str = ""                   # Soldado, Druida, Mago, Paladín, etc.
    raza: str = ""                    # Elfo, Enano, Humano, etc.
    level: int = 0                    # Nivel actual

    # Vitals (HP/MP/Energía)
    hp: int = 0
    maxhp: int = 0
    hp_pct: int = 0                   # Porcentaje (0-100) — para triggers
    mp: int = 0
    maxmp: int = 0
    mp_pct: int = 0
    energy: int = 0
    energy_pct: int = 0

    # Combat State
    in_combat: bool = False
    is_target: bool = False           # ¿Es objetivo/enemigo del ataque?
    last_attacker: str = ""           # Quién me atacó

    # Buffs/Debuffs (for storage-only triggers)
    buffs: list[str] = field(default_factory=list)     # ["Fuerza", "Escudo", ...]
    debuffs: list[str] = field(default_factory=list)   # ["Veneno", "Maldición", ...]

    # History (para evitar spam y almacenar)
    last_state: str = ""              # Último estado anunciado (para evitar spam)
    state_history: list[str] = field(default_factory=list)  # Histórico de cambios

    # Spam Prevention Flags (como en VipMud)
    # Maps threshold (100, 90, 60, 30, 10) to whether we've already announced it
    hp_threshold_flags: dict[int, bool] = field(
        default_factory=lambda: {100: False, 90: False, 60: False, 30: False, 10: False}
    )

    def should_announce_hp_threshold(self, threshold: int) -> bool:
        """Check if we should announce this HP threshold (and mark it announced)."""
        if self.hp_threshold_flags.get(threshold, False):
            return False  # Already announced
        self.hp_threshold_flags[threshold] = True
        return True

    def reset_hp_thresholds(self):
        """Reset HP threshold flags when HP increases significantly."""
        for key in self.hp_threshold_flags:
            self.hp_threshold_flags[key] = False

    def update_vitals(self, hp: int, maxhp: int, mp: int = 0, maxmp: int = 0):
        """Update HP/MP and recalculate percentages."""
        self.hp = hp
        self.maxhp = maxhp
        self.hp_pct = int((hp / maxhp * 100)) if maxhp > 0 else 0

        if mp > 0 or maxmp > 0:
            self.mp = mp
            self.maxmp = maxmp
            self.mp_pct = int((mp / maxmp * 100)) if maxmp > 0 else 0

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

# Triggers Reference - Diseño y Variables de Estado

## Contexto: VipMud Estados.set

El archivo `Scripts/Reinos de leyenda/ScripsRL/Estados.set` es la referencia principal. Define cómo se gestiona el estado del personaje y otros personajes en combate.

### Variables de Estado en VipMud

```
FlagEstados        → Bandera de control (contador de eventos)
HistorialEstados   → Lista de cambios de estado (para almacenar/visualizar)
UltimoEstado       → Último estado registrado (para logging)
PorcentajeEstado   → HP actual como porcentaje (0-100)
PersonajeEstado    → Nombre del personaje afectado (tu PJ o enemigo)
EnergiaEstado      → Energía como porcentaje (si existe)
FlagEA100, FlagEA90, FlagEA60, FlagEA30  → Flags para aliados (evitan spam)
FlagEE100, FlagEE90, FlagEE60, FlagEE30  → Flags para enemigos (evitan spam)
```

### Patrón de Triggers en VipMud

```
IF HP >= 90%:
  IF es aliado:
    PLAY sound "Estado aliado 100.wav" (pan derecha)
    SET FlagEA100 = 1 (evita spam)
  ELSE (es enemigo):
    PLAY sound "Estado enemigo 100.wav" (pan izquierda)
    SET FlagEE100 = 1

IF 60% <= HP < 90%:
  [similar para rango 90%]

IF 30% <= HP < 60%:
  [similar para rango 60%]

IF HP < 30%:
  CALL evento especial (healing, evacuar, etc.)
```

---

## VipZhyla: CharacterState Model

Basado en el patrón de VipMud, la estructura debe ser:

```python
@dataclass
class CharacterState:
    # Identidad
    name: str = ""                    # Nombre del PJ
    clase: str = ""                   # Soldado, Druida, Mago, etc.
    raza: str = ""                    # Elfo, Enano, Humano, etc.
    level: int = 0                    # Nivel
    
    # Vitales (HP/MP/Energía)
    hp: int = 0
    maxhp: int = 0
    hp_pct: int = 0                   # Porcentaje (0-100) — para triggers
    mp: int = 0
    maxmp: int = 0
    mp_pct: int = 0
    energy: int = 0
    energy_pct: int = 0
    
    # Estado de Combate
    in_combat: bool = False
    is_target: bool = False           # ¿Es objetivo/enemigo?
    last_attacker: str = ""           # Quién me atacó
    
    # Buffs/Debuffs
    buffs: list[str] = field(default_factory=list)  # ["Fuerza", "Escudo", ...]
    debuffs: list[str] = field(default_factory=list) # ["Veneno", "Maldición", ...]
    
    # Historial (para gagging y almacenamiento)
    last_state: str = ""              # Último estado anunciado (para evitar spam)
    state_history: list[str] = field(default_factory=list)  # Histórico
    
    # Flags para evitar spam (como en VipMud)
    hp_threshold_flags: dict[int, bool] = field(default_factory=lambda: {
        100: False, 90: False, 60: False, 30: False, 10: False
    })  # {100: False, 90: False, ...} para cada umbral
```

---

## Triggers Coherentes con VipMud

### Trigger 1: Monitor HP (Solo Sonidos, Sin TTS - Storage)

**Función:** Reproducir sonidos cuando HP cambia de rango. NO anunciar por voz (solo almacenar).

```json
{
  "id": "trg_hp_monitor",
  "name": "HP Monitor - Sonidos",
  "pattern": "",
  "is_regex": false,
  "enabled": true,
  "triggers_on": "hp_pct_change",
  "conditions": [
    {"field": "hp_pct", "operator": "changed", "value": null}
  ],
  "actions": [
    {
      "action_type": "sound",
      "value": "RL/Combate/Estado aliado {hp_threshold}.wav",
      "only_if": "not in_combat"
    },
    {
      "action_type": "storage",
      "value": "hp_threshold_flags",
      "description": "Guardar qué rango ya reproducimos"
    }
  ]
}
```

**Variables necesarias:**
- `hp_pct` — calculado de hp/maxhp
- `hp_threshold` — 100, 90, 60, 30, 10 (extraído de hp_pct)
- `in_combat` — booleano
- `hp_threshold_flags` — dict para evitar spam

---

### Trigger 2: Alerta Vida Baja (TTS + GAG)

**Función:** Anunciar cuando tu vida baja de 30%, gagging el output original.

```json
{
  "id": "trg_low_health_alert",
  "name": "Alerta: Vida Baja",
  "pattern": "Your health is low|Tienes poca vida",
  "is_regex": true,
  "enabled": true,
  "conditions": [
    {"field": "hp_pct", "operator": "<", "value": 30},
    {"field": "in_combat", "operator": "==", "value": true}
  ],
  "actions": [
    {
      "action_type": "tts",
      "value": "ALERTA: Vida crítica. HP: {hp}/{maxhp}"
    },
    {
      "action_type": "gag",
      "value": null,
      "description": "Gagging línea original del MUD"
    }
  ]
}
```

**Variables necesarias:**
- `hp_pct` — comparación condicional
- `in_combat` — booleano
- `hp` / `maxhp` — para interpolar en TTS

---

### Trigger 3: Detectar Envenenamiento (Clase Específica)

**Función:** Anunciar diferente según clase.

```json
{
  "id": "trg_poison_class_aware",
  "name": "Detección Veneno (Sensible a Clase)",
  "pattern": "You are poisoned|Estás envenenado",
  "is_regex": true,
  "enabled": true,
  "conditions": [
    {"field": "clase", "operator": "in", "value": ["Druida", "Paladín"]}
  ],
  "actions": [
    {
      "action_type": "tts",
      "value": "VENENO: Como {clase}, necesitas contraataque mágico inmediato",
      "only_if": "clase in ['Druida', 'Paladín']"
    },
    {
      "action_type": "storage",
      "value": "debuffs",
      "operation": "add",
      "data": "Veneno",
      "description": "Guardar en lista de debuffs"
    }
  ]
}
```

**Variables necesarias:**
- `clase` — para condicionales
- `debuffs` — lista para almacenar estado

---

### Trigger 4: Detectar Buff (Storage Solo)

**Función:** Registrar buff sin anunciar (para consultar después en triggers posteriores).

```json
{
  "id": "trg_buff_tracker",
  "name": "Buff Tracker (Storage)",
  "pattern": "You are blessed|You feel stronger|Estás bendecido",
  "is_regex": true,
  "enabled": true,
  "no_announce": true,
  "actions": [
    {
      "action_type": "storage",
      "value": "buffs",
      "operation": "add",
      "data": "{matched_buff_name}",
      "description": "Añadir buff a lista"
    }
  ]
}
```

**Variables necesarias:**
- `buffs` — lista para almacenar
- `matched_buff_name` — extraído del patrón

---

### Trigger 5: Combate Crítico (Multi-Acción)

**Función:** Al entrar en combate crítico, múltiples acciones.

```json
{
  "id": "trg_critical_combat",
  "name": "Combate Crítico",
  "triggers_on": "combat_state_change",
  "conditions": [
    {"field": "in_combat", "operator": "==", "value": true},
    {"field": "hp_pct", "operator": "<", "value": 50}
  ],
  "actions": [
    {
      "action_type": "tts",
      "value": "COMBATE CRÍTICO: {clase} en peligro",
      "priority": "high"
    },
    {
      "action_type": "sound",
      "value": "RL/Combate/Estado critico.wav"
    },
    {
      "action_type": "storage",
      "value": "last_combat_alert",
      "data": "{timestamp}",
      "description": "Timestamp para cooldown"
    }
  ]
}
```

**Variables necesarias:**
- `in_combat` — booleano
- `hp_pct` — para comparación
- `clase` — para TTS personalizado
- `timestamp` — para cooldown

---

## Tipos de Triggers (Clasificación)

### 1. **SONIDO SOLO** (Sin TTS)
- Reproducir sonido según HP rango
- Reproducir sonido de alerta
- Variable flags para evitar spam
- NO anunciar (silencioso para lector)

### 2. **ALMACENAMIENTO/TRACKING** (No anunciar)
- Guardar buff en lista
- Guardar debuff en lista
- Guardar timestamp de evento
- Guardar contador de algo
- **Acción:** Storage, no TTS

### 3. **ANUNCIO + GAG** (TTS + ocultar output)
- Anunciar alerta
- Ocultar línea original del MUD
- Reemplazar output con versión amigable

### 4. **CONDICIONAL + MULTICLASE** (Logic)
- Si eres Druida → reacción A
- Si eres Guerrero → reacción B
- Incluir `clase` en condiciones

### 5. **TIMER/COOLDOWN** (Control de Spam)
- No reproducir cada N segundos
- Usar flags (como en VipMud)
- Almacenar último timestamp

---

## Variables de CharacterState (Resumen)

**VITALES:**
- `hp`, `maxhp`, `hp_pct` (0-100)
- `mp`, `maxmp`, `mp_pct`
- `energy`, `energy_pct`

**IDENTIDAD:**
- `name`, `clase`, `raza`, `level`

**COMBATE:**
- `in_combat` (bool)
- `is_target` (bool)
- `last_attacker` (string)

**ESTADO:**
- `buffs` (list) — para storage
- `debuffs` (list) — para storage
- `hp_threshold_flags` (dict) — para evitar spam

**HISTÓRICO:**
- `last_state` (string) — última línea anunciada
- `state_history` (list) — histórico de cambios

---

## Patrones a EVITAR (No como en VipMud Legacy)

❌ **No hacer:**
- Triggers con TTS para CADA HP % (spam infinito)
- Anunciar buffs aplicados (spam en combate)
- Gagging sin necesidad (ocultar info útil)

✅ **Hacer (como VipMud):**
- Sonidos para HP ranges, con flags para evitar spam
- Almacenar buffs/debuffs sin anunciar (query después)
- Gagging solo cuando hay reemplazo o es spam obvio
- Anunciar solo cambios significativos (transiciones, críticos)

---

## Resumen: Lo que Implementar

1. **CharacterState dataclass** con las variables listadas
2. **Trigger UI improvements:**
   - Permitir triggers que se activen por eventos (no solo pattern match)
   - Permitir condiciones complejas (HP < 30% AND in_combat)
   - Permitir acciones de storage (no solo TTS/GAG)
3. **Parser mejorado** para extraer clase/raza del output MUD
4. **Ejemplo triggers** basados en estos patrones
5. **Triggers predefinidos** (triggers.json de ejemplo)

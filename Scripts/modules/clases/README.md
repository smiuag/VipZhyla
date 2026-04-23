# Reinos de Leyenda - Character Classes

## Overview

This directory contains class definitions for all 24 character classes in Reinos de Leyenda.
Each class is a Lua module that inherits from `base.lua`.

## Current Implementation

### ✅ Implemented (3/24)
1. **chamanes.lua** - Shaman (spellcasters, fire/lightning, healing)
2. **paladines.lua** - Paladin (holy warriors, divine magic, buffs)
3. **khazads.lua** - Dwarf (melee combat, mining, stone magic)

### ⏳ TODO (21/24)
- Soldados (Warriors)
- Magos (Wizards)
- Clérigos (Clerics)
- Druidas (Druids)
- Bardo (Bard)
- Asesino (Assassin)
- Ranger
- Monje (Monk)
- Nigromante (Necromancer)
- Guerrero de la Luz (Lightbringer)
- Sacerdote de la Oscuridad (Duskpriest)
- Templario (Templar)
- Hechicero (Warlock)
- Brujo (Witch)
- Alquimista (Alchemist)
- Cazador de Dragones (Dragon Slayer)
- Ermitaño (Hermit)
- Trovador (Troubador)
- Corsario (Corsair)
- Espadachín (Swordmaster)
- Caballero Oscuro (Dark Knight)
- Clérigo de Batalla (Battle Cleric)

## How to Add a New Class

### 1. Create the Class File

Copy `chamanes.lua` as a template:

```bash
cp chamanes.lua nombredelclase.lua
```

### 2. Define Class Stats

Edit your new file and update:

```lua
local NewClass = ClassBase.new("Nombre de la Clase")

-- Add specific stat bonuses
NewClass:add_passive_bonus("strength", 2)      -- Bonus to strength
NewClass:add_passive_bonus("dexterity", 1)     -- Bonus to dexterity
```

**Stat names available:**
- `strength` - Physical power
- `dexterity` - Accuracy, dodge, agility
- `constitution` - Health/durability
- `intelligence` - Mana, spell damage
- `wisdom` - Perception, healing
- `charisma` - Leadership, NPC reactions

### 3. Add Class Abilities

```lua
NewClass:add_ability("Ability Name", "Descripción", "tipo")
NewClass:add_ability("Power Strike", "Golpe poderoso", "physical")
NewClass:add_ability("Heal", "Curación", "heal")
```

**Valid ability types:**
- `spell` - Magic spell
- `physical` - Melee attack
- `heal` - Healing magic
- `buff` - Positive effect
- `debuff` - Negative effect
- `summon` - Summon creature
- `control` - Control/disable
- `area` - Area of effect
- `special` - Special/unique

### 4. Implement detect_ability()

Add pattern matching for class-specific abilities:

```lua
function M.detect_ability(text)
    local text_lower = text:lower()

    if text_lower:match("ability name") then
        return { name = "Ability Name", type = "physical" }
    end
    
    return nil
end
```

### 5. Example: Complete Warrior Class

```lua
local ClassBase = require("modules.clases.base")
local M = {}

local Warrior = ClassBase.new("Soldado")

-- Bonuses
Warrior:add_passive_bonus("strength", 3)
Warrior:add_passive_bonus("constitution", 1)

-- Abilities
Warrior:add_ability("Slash", "Tajo", "physical")
Warrior:add_ability("Power Attack", "Ataque poderoso", "physical")
Warrior:add_ability("Shield Wall", "Muro de escudos", "buff")
Warrior:add_ability("Whirlwind Attack", "Ataque giratorio", "area")

function M.init(game)
    vipzhyla.say("[SOLDADOS] Habilidades del Soldado cargadas")
end

function M.get_class()
    return Warrior
end

function M.get_abilities()
    return Warrior:get_abilities()
end

function M.detect_ability(text)
    local text_lower = text:lower()
    
    if text_lower:match("tajo") then
        return { name = "Slash", type = "physical" }
    elseif text_lower:match("poderoso") then
        return { name = "Power Attack", type = "physical" }
    elseif text_lower:match("escudo") then
        return { name = "Shield Wall", type = "buff" }
    elseif text_lower:match("giratorio") then
        return { name = "Whirlwind Attack", type = "area" }
    end
    
    return nil
end

return M
```

## Integration in Main Game

Classes are auto-loaded in `reinos_de_leyenda.lua` via:

```lua
-- In game.init():
game.init_module("clases.paladines")
game.init_module("clases.chamanes")
-- etc...
```

Or dynamically loaded based on character class selection.

## Testing a New Class

```bash
python -c "
from src.scripting import ScriptLoader
loader = ScriptLoader()
loader.load_scripts()
# Test class detection
"
```

## Pattern Matching Tips

- Use `%lower()` for case-insensitive matching
- Reference `habilidades.lua` for common patterns
- Test with sample MUD text to ensure detection works
- Keep patterns specific to avoid false positives

## VipMud Reference

Refer to `Scripts/Clases/` for original VipMud implementations:
- Each `.set` file contains triggers for that class's abilities
- Look for ability names in Spanish
- Study pattern matching (text contains "X")

## Contributing

When you implement a new class:
1. Test with real MUD gameplay if possible
2. Add ability detection patterns
3. Document any special mechanics
4. Update this README with completion status
5. Commit with: `"Implement [ClassName] class module"`

## Completed Classes by Contributor

| Class | Date | Lines | Abilities |
|-------|------|-------|-----------|
| Chamanes | 2026-04-24 | 70 | 9 |
| Paladines | 2026-04-24 | 72 | 10 |
| Khazads | 2026-04-24 | 68 | 9 |
| | | | |

---

**Goal:** All 24 classes implemented and fully functional by 2026-06-30

Current progress: 3/24 (12.5%)

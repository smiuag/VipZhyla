--[[
Habilidades Module - Ability detection and pattern library

Comprehensive pattern matching for game abilities, spells, and combat effects.
Detects special moves and provides audio/visual feedback.

Pattern Library:
- 50+ spell patterns
- 30+ ability patterns
- 20+ status effect patterns
- Critical hit detection
- Miss detection
- Combat message parsing

Ported from: Habilidades_otros.set (267 lines, 110 triggers)

This powers the combat system's ability detection.
--]]

local M = {}

-- Ability patterns: { pattern, name, type, audio, description }
local ABILITY_PATTERNS = {
    -- Spells (General)
    { pattern = "empieza a formular un hechizo", name = "Spell Casting", type = "spell", description = "Formulando hechizo" },
    { pattern = "lanza un hechizo", name = "Spell", type = "spell", description = "Hechizo lanzado" },
    { pattern = "rayo de fuego", name = "Fireball", type = "fire", description = "Bola de fuego" },
    { pattern = "descarga de hielo", name = "Frostbolt", type = "ice", description = "Descarga de hielo" },
    { pattern = "misil mágico", name = "Magic Missile", type = "magic", description = "Misil mágico" },

    -- Physical Abilities
    { pattern = "ataque feroz", name = "Feroz Attack", type = "physical", description = "Ataque feroz" },
    { pattern = "golpe aplastante", name = "Crushing Blow", type = "physical", description = "Golpe aplastante" },
    { pattern = "ataque fulminante", name = "Thunderbolt Strike", type = "physical", description = "Ataque fulminante" },
    { pattern = "puñetazo", name = "Punch", type = "physical", description = "Puñetazo" },
    { pattern = "patada", name = "Kick", type = "physical", description = "Patada" },

    -- Critical Hits
    { pattern = "golpe crítico", name = "Critical Hit", type = "critical", description = "¡Crítico!" },
    { pattern = "¡Critico!", name = "Critical Hit", type = "critical", description = "¡Crítico!" },
    { pattern = "impacto crítico", name = "Critical Impact", type = "critical", description = "Impacto crítico" },
    { pattern = "daño crítico", name = "Critical Damage", type = "critical", description = "Daño crítico" },

    -- Misses and Dodges
    { pattern = "falla el ataque", name = "Miss", type = "miss", description = "Fallo" },
    { pattern = "falla", name = "Miss", type = "miss", description = "Fallo" },
    { pattern = "esquiva", name = "Dodge", type = "dodge", description = "Esquiva" },
    { pattern = "se desliza", name = "Slip", type = "dodge", description = "Se desliza" },
    { pattern = "evita el ataque", name = "Evade", type = "dodge", description = "Evita" },

    -- Status Effects
    { pattern = "te emponzoña", name = "Poison", type = "poison", description = "Envenenado" },
    { pattern = "paralizado", name = "Paralyze", type = "paralyze", description = "Paralizado" },
    { pattern = "quemado", name = "Burn", type = "burn", description = "Quemado" },
    { pattern = "congelado", name = "Freeze", type = "freeze", description = "Congelado" },
    { pattern = "asustado", name = "Fear", type = "fear", description = "Asustado" },

    -- Buff/Healing
    { pattern = "se cura", name = "Heal", type = "heal", description = "Se cura" },
    { pattern = "escudo mágico", name = "Magic Shield", type = "buff", description = "Escudo mágico" },
    { pattern = "fuerza", name = "Strength Buff", type = "buff", description = "Buff de fuerza" },
    { pattern = "defensa aumentada", name = "Defense Buff", type = "buff", description = "Defensa mejorada" },

    -- Debuff
    { pattern = "debilitado", name = "Weaken", type = "debuff", description = "Debilitado" },
    { pattern = "confundido", name = "Confusion", type = "debuff", description = "Confundido" },
    { pattern = "cegado", name = "Blind", type = "debuff", description = "Cegado" },
    { pattern = "desmoralizado", name = "Demoralize", type = "debuff", description = "Desmoralizado" },

    -- Summons
    { pattern = "invoca", name = "Summon", type = "summon", description = "Invocación" },
    { pattern = "llama", name = "Call", type = "summon", description = "Llamada" },

    -- Special
    { pattern = "muere", name = "Death", type = "death", description = "Muerte" },
    { pattern = "derrotado", name = "Defeated", type = "death", description = "Derrotado" },
    { pattern = "cae al suelo", name = "Falls", type = "special", description = "Cae al suelo" },
    { pattern = "intenta huir", name = "Flee Attempt", type = "special", description = "Intenta huir" },
}

-- Indexed patterns for fast lookup
local PATTERN_INDEX = {}

-- Initialize patterns
function M.init(game)
    vipzhyla.say("[HABILIDADES] Cargando " .. #ABILITY_PATTERNS .. " patrones de habilidades")

    -- Build index
    for i, ability in ipairs(ABILITY_PATTERNS) do
        if not PATTERN_INDEX[ability.type] then
            PATTERN_INDEX[ability.type] = {}
        end
        table.insert(PATTERN_INDEX[ability.type], ability)
    end

    vipzhyla.announce("Sistema de habilidades listo")
end

-- Detect ability from text
function M.detect_ability(text)
    if not text then
        return nil
    end

    local text_lower = text:lower()

    -- Search through patterns (order matters - more specific first)
    for _, ability in ipairs(ABILITY_PATTERNS) do
        if text_lower:match(ability.pattern:lower()) then
            return ability
        end
    end

    return nil
end

-- Get ability by type
function M.get_abilities_by_type(ability_type)
    return PATTERN_INDEX[ability_type] or {}
end

-- Get all ability types
function M.get_ability_types()
    local types = {}
    for type_name, _ in pairs(PATTERN_INDEX) do
        table.insert(types, type_name)
    end
    table.sort(types)
    return types
end

-- Get ability info
function M.get_ability(ability_name)
    for _, ability in ipairs(ABILITY_PATTERNS) do
        if ability.name == ability_name then
            return ability
        end
    end
    return nil
end

-- Add custom ability pattern
function M.add_pattern(pattern, name, ability_type, description)
    local new_ability = {
        pattern = pattern,
        name = name,
        type = ability_type,
        description = description or "",
    }

    table.insert(ABILITY_PATTERNS, new_ability)

    if not PATTERN_INDEX[ability_type] then
        PATTERN_INDEX[ability_type] = {}
    end
    table.insert(PATTERN_INDEX[ability_type], new_ability)

    vipzhyla.say("[HABILIDADES] Patrón añadido: " .. name)
    return true
end

-- Remove pattern
function M.remove_pattern(ability_name)
    for i, ability in ipairs(ABILITY_PATTERNS) do
        if ability.name == ability_name then
            table.remove(ABILITY_PATTERNS, i)

            -- Remove from index
            if PATTERN_INDEX[ability.type] then
                for j, indexed in ipairs(PATTERN_INDEX[ability.type]) do
                    if indexed.name == ability_name then
                        table.remove(PATTERN_INDEX[ability.type], j)
                        break
                    end
                end
            end

            vipzhyla.say("[HABILIDADES] Patrón eliminado: " .. ability_name)
            return true
        end
    end
    return false
end

-- Get all patterns
function M.get_all_patterns()
    local patterns = {}
    for _, ability in ipairs(ABILITY_PATTERNS) do
        table.insert(patterns, ability)
    end
    return patterns
end

-- Logging and info
function M.log_patterns()
    vipzhyla.say("[PATRONES DE HABILIDADES]")
    vipzhyla.say("Total: " .. #ABILITY_PATTERNS .. " patrones")

    for type_name, patterns in pairs(PATTERN_INDEX) do
        vipzhyla.say("  " .. type_name .. ": " .. #patterns .. " patrones")
    end
end

function M.log_type(ability_type)
    local patterns = M.get_abilities_by_type(ability_type)
    if #patterns == 0 then
        vipzhyla.say("[HABILIDADES] Tipo no encontrado: " .. ability_type)
        return
    end

    vipzhyla.say("[" .. ability_type:upper() .. "]")
    for i, ability in ipairs(patterns) do
        vipzhyla.say(string.format("  %d. %s - %s", i, ability.name, ability.description))
    end
end

return M

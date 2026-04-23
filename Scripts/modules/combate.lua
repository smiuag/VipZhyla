--[[
Combate Module - Combat system and battle automation

Manages:
- Combat detection and state tracking
- Enemy detection and tracking
- Ability pattern matching from text
- Combat triggers (hits, misses, criticals, etc.)
- Health alerts during combat
- Combat audio feedback

Combat Patterns:
- "X ataca..." = attack incoming
- "¡Golpe crítico!" = critical hit
- "falla" = attack missed
- "te alcanza" = hit taken
- "empieza a formular" = spell cast

Ported from: Combate.set (333 lines, 92 triggers)
            Habilidades_otros.set (267 lines, 110 triggers)

Note: Full Lua pattern library in Phase 6E
--]]

local M = {}

-- Combat state
local COMBAT_STATE = {
    active = false,
    current_enemy = "",
    enemies = {},
    allies = {},
    last_attack_time = 0,
    attack_count = 0,
    health_critical = 30,  -- Alert threshold %
}

-- Combat statistics
local COMBAT_STATS = {
    total_hits = 0,
    total_misses = 0,
    total_criticals = 0,
    damage_taken = 0,
    damage_dealt = 0,
}

-- Ability patterns (simplified for MVP)
local ABILITY_PATTERNS = {
    -- Format: { pattern = "regex", name = "ability name", type = "damage|heal|buff|debuff" }
    { pattern = "empieza a formular un hechizo", name = "Spell", type = "magic" },
    { pattern = "ataque feroz", name = "Feroz Attack", type = "damage" },
    { pattern = "golpe crítico", name = "Critical Hit", type = "critical" },
    { pattern = "falla", name = "Miss", type = "miss" },
    { pattern = "te alcanza", name = "Hit", type = "hit" },
}

-- Initialize module
function M.init(game)
    vipzhyla.say("[COMBATE] Sistema de combate inicializado")
    vipzhyla.say("[COMBATE] Detectando patrones de combate...")
end

-- Handle MUD text for combat patterns
function M.on_message(channel, text)
    if channel == "sala" then
        M.detect_combat_patterns(text)
    end
end

-- Handle GMCP for health tracking during combat
function M.on_gmcp(module_name, data)
    if module_name == "Char.Vitals" and COMBAT_STATE.active then
        M.check_health_during_combat(data)
    end
end

-- Detect combat patterns from text
function M.detect_combat_patterns(text)
    -- Check each pattern
    for _, ability in ipairs(ABILITY_PATTERNS) do
        if text:match(ability.pattern) then
            M.on_ability_detected(text, ability)
            return
        end
    end

    -- Check for entering/exiting combat
    if text:match("ataque") and not COMBAT_STATE.active then
        M.enter_combat("Enemigo desconocido")
    elseif text:match("muere") and COMBAT_STATE.active then
        M.exit_combat()
    elseif text:match("huyes") and COMBAT_STATE.active then
        M.exit_combat()
    end
end

-- Called when ability is detected
function M.on_ability_detected(text, ability)
    vipzhyla.say("[COMBATE] " .. ability.name .. ": " .. text:sub(1, 50) .. "...")

    -- Update statistics
    if ability.type == "critical" then
        COMBAT_STATS.total_criticals = COMBAT_STATS.total_criticals + 1
    elseif ability.type == "miss" then
        COMBAT_STATS.total_misses = COMBAT_STATS.total_misses + 1
    elseif ability.type == "hit" then
        COMBAT_STATS.total_hits = COMBAT_STATS.total_hits + 1
    end
end

-- Check health during combat
function M.check_health_during_combat(vitals_data)
    local hp = vitals_data.hp or 0
    local maxhp = vitals_data.maxhp or 0

    if maxhp == 0 then
        return
    end

    local health_percent = (hp / maxhp) * 100

    -- Alert if critical
    if health_percent < COMBAT_STATE.health_critical then
        vipzhyla.announce("¡ALERTA! Vida crítica en combate: " .. hp .. " de " .. maxhp)
    end
end

-- Enter combat
function M.enter_combat(enemy_name)
    if COMBAT_STATE.active then
        return  -- Already in combat
    end

    COMBAT_STATE.active = true
    COMBAT_STATE.current_enemy = enemy_name
    table.insert(COMBAT_STATE.enemies, enemy_name)

    -- Reset stats for this combat
    COMBAT_STATS.total_hits = 0
    COMBAT_STATS.total_misses = 0
    COMBAT_STATS.total_criticals = 0
    COMBAT_STATS.damage_taken = 0
    COMBAT_STATS.damage_dealt = 0

    COMBAT_STATE.last_attack_time = os.time()

    vipzhyla.announce("¡Combate iniciado con " .. enemy_name .. "!")
end

-- Exit combat
function M.exit_combat()
    if not COMBAT_STATE.active then
        return  -- Not in combat
    end

    COMBAT_STATE.active = false

    -- Log combat summary
    vipzhyla.announce("Combate finalizado")
    M.log_combat_summary()

    COMBAT_STATE.enemies = {}
    COMBAT_STATE.current_enemy = ""
end

-- Add enemy to combat
function M.add_enemy(enemy_name)
    local exists = false
    for _, e in ipairs(COMBAT_STATE.enemies) do
        if e == enemy_name then
            exists = true
            break
        end
    end

    if not exists then
        table.insert(COMBAT_STATE.enemies, enemy_name)
        vipzhyla.say("[COMBATE] Enemigo detectado: " .. enemy_name)
    end
end

-- Remove enemy from combat
function M.remove_enemy(enemy_name)
    for i, e in ipairs(COMBAT_STATE.enemies) do
        if e == enemy_name then
            table.remove(COMBAT_STATE.enemies, i)
            vipzhyla.say("[COMBATE] Enemigo derrotado: " .. enemy_name)
            break
        end
    end
end

-- Add ally
function M.add_ally(ally_name)
    local exists = false
    for _, a in ipairs(COMBAT_STATE.allies) do
        if a == ally_name then
            exists = true
            break
        end
    end

    if not exists then
        table.insert(COMBAT_STATE.allies, ally_name)
    end
end

-- Get combat status
function M.is_in_combat()
    return COMBAT_STATE.active
end

function M.get_current_enemy()
    return COMBAT_STATE.current_enemy
end

function M.get_enemies()
    return COMBAT_STATE.enemies
end

function M.get_allies()
    return COMBAT_STATE.allies
end

-- Get combat statistics
function M.get_stats()
    return COMBAT_STATS
end

-- Log combat statistics
function M.log_combat_summary()
    local total = COMBAT_STATS.total_hits + COMBAT_STATS.total_misses
    if total == 0 then
        return
    end

    local accuracy = (COMBAT_STATS.total_hits / total) * 100

    vipzhyla.say("[ESTADÍSTICAS DE COMBATE]")
    vipzhyla.say("  Golpes: " .. COMBAT_STATS.total_hits)
    vipzhyla.say("  Fallos: " .. COMBAT_STATS.total_misses)
    vipzhyla.say("  Críticos: " .. COMBAT_STATS.total_criticals)
    vipzhyla.say("  Precisión: " .. string.format("%.1f", accuracy) .. "%")
end

function M.log_status()
    if not COMBAT_STATE.active then
        vipzhyla.say("[COMBATE] No estás en combate")
        return
    end

    vipzhyla.say("[COMBATE ACTIVO]")
    vipzhyla.say("  Enemigo actual: " .. COMBAT_STATE.current_enemy)
    vipzhyla.say("  Enemigos totales: " .. #COMBAT_STATE.enemies)
    if #COMBAT_STATE.allies > 0 then
        vipzhyla.say("  Aliados: " .. table.concat(COMBAT_STATE.allies, ", "))
    end
    vipzhyla.say("  Golpes: " .. COMBAT_STATS.total_hits)
    vipzhyla.say("  Fallos: " .. COMBAT_STATS.total_misses)
end

-- Reset combat state
function M.reset()
    COMBAT_STATE.active = false
    COMBAT_STATE.current_enemy = ""
    COMBAT_STATE.enemies = {}
    COMBAT_STATE.allies = {}

    COMBAT_STATS.total_hits = 0
    COMBAT_STATS.total_misses = 0
    COMBAT_STATS.total_criticals = 0
    COMBAT_STATS.damage_taken = 0
    COMBAT_STATS.damage_dealt = 0

    vipzhyla.say("[COMBATE] Estado reset")
end

return M

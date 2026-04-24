--[[
Magia/Magic System - Spell casting and magic management

Manages spell casting, mana/spell points, cooldowns, and magic effects.

Phase 7A: Complete game state management
]]

local M = {}

-- Magic schools (for Reinos de Leyenda)
local MAGIC_SCHOOLS = {
    arcana = "Arcana",
    fuego = "Fuego",
    hielo = "Hielo",
    electricidad = "Electricidad",
    naturaleza = "Naturaleza",
    sanacion = "Sanacion",
    oscuridad = "Oscuridad",
    luz = "Luz",
}

-- Spell database
local SPELLS = {
    -- Arcana School
    missile_magico = {
        name = "Misil Magico",
        school = "arcana",
        cost = 10,           -- mana cost
        cooldown = 5,        -- seconds
        description = "Basic arcane projectile",
        castable = true,
    },
    escudo_magico = {
        name = "Escudo Magico",
        school = "arcana",
        cost = 15,
        cooldown = 30,
        description = "Magical shield",
        castable = true,
    },
    teletransporte = {
        name = "Teletransporte",
        school = "arcana",
        cost = 50,
        cooldown = 60,
        description = "Teleport to location",
        castable = true,
    },

    -- Fire School
    bola_fuego = {
        name = "Bola de Fuego",
        school = "fuego",
        cost = 20,
        cooldown = 10,
        description = "Fireball attack",
        castable = true,
    },
    inferno = {
        name = "Inferno",
        school = "fuego",
        cost = 40,
        cooldown = 45,
        description = "Massive fire damage",
        castable = true,
    },

    -- Ice School
    rayo_hielo = {
        name = "Rayo de Hielo",
        school = "hielo",
        cost = 18,
        cooldown = 8,
        description = "Ice ray attack",
        castable = true,
    },
    congelacion = {
        name = "Congelacion",
        school = "hielo",
        cost = 35,
        cooldown = 40,
        description = "Freeze enemy",
        castable = true,
    },

    -- Healing School
    sanacion_menor = {
        name = "Sanacion Menor",
        school = "sanacion",
        cost = 12,
        cooldown = 3,
        description = "Heal small amount",
        castable = true,
    },
    sanacion_mayor = {
        name = "Sanacion Mayor",
        school = "sanacion",
        cost = 30,
        cooldown = 20,
        description = "Heal large amount",
        castable = true,
    },
    resurreccion = {
        name = "Resurrección",
        school = "sanacion",
        cost = 100,
        cooldown = 300,
        description = "Revive fallen ally",
        castable = true,
    },
}

-- Spell casting patterns
local SPELL_PATTERNS = {
    bola_fuego = {
        "lanzas una bola de fuego",
        "fireball strikes",
        "bola de fuego",
    },
    escudo_magico = {
        "escudo magico te rodea",
        "magical shield surrounds",
        "escudo de energia",
    },
    sanacion_menor = {
        "Sientes una sanacion",
        "healing energy",
        "te sientes mejor",
        "curacion",
    },
    teletransporte = {
        "desapareces en",
        "you vanish in",
        "teletransporte",
    },
}

-- Player magic state
local magic_state = {
    mana = 100,
    max_mana = 100,
    mana_regen = 1,        -- per second
    last_mana_regen = os.time(),
    spell_cooldowns = {},  -- spell_name -> expiration_time
}

-- Known spells (unlocked spells)
local known_spells = {}

function M.init(game)
    game.magia = game.magia or {}
    game.magia.state = magic_state
    game.magia.spells = SPELLS
    game.magia.known = known_spells

    -- Initialize with common spells
    for spell_name, _ in pairs(SPELLS) do
        known_spells[spell_name] = true
    end
end

--[[ ===== Mana Management ===== ]]

function M.set_mana(current, max)
    --[[Set current and max mana.]]
    magic_state.mana = current
    magic_state.max_mana = max
end

function M.get_mana()
    --[[Get current mana amount.]]
    return magic_state.mana
end

function M.get_max_mana()
    --[[Get maximum mana.]]
    return magic_state.max_mana
end

function M.get_mana_percent()
    --[[Get mana as percentage of max.]]
    return (magic_state.mana / magic_state.max_mana) * 100
end

function M.restore_mana(amount)
    --[[Restore mana by amount.]]
    magic_state.mana = math.min(magic_state.mana + amount, magic_state.max_mana)
    vipzhyla.announce("Mana restored: " .. amount)
end

function M.drain_mana(amount)
    --[[Drain mana by amount.]]
    if magic_state.mana >= amount then
        magic_state.mana = magic_state.mana - amount
        return true
    end
    return false
end

function M.is_mana_available(amount)
    --[[Check if enough mana available.]]
    return magic_state.mana >= amount
end

--[[ ===== Spell Casting ===== ]]

function M.cast_spell(spell_name, target)
    --[[
    Attempt to cast spell.

    Args:
        spell_name: Spell to cast (e.g., "bola_fuego")
        target: Optional target name

    Returns:
        true if cast successfully
    ]]

    -- Check if spell exists
    if not SPELLS[spell_name] then
        vipzhyla.announce("Hechizo desconocido: " .. spell_name)
        return false
    end

    local spell = SPELLS[spell_name]

    -- Check if spell is known
    if not known_spells[spell_name] then
        vipzhyla.announce("No conoces este hechizo")
        return false
    end

    -- Check if castable
    if not spell.castable then
        vipzhyla.announce("No puedes lanzar este hechizo")
        return false
    end

    -- Check cooldown
    local cooldown_until = magic_state.spell_cooldowns[spell_name]
    if cooldown_until and os.time() < cooldown_until then
        local remaining = cooldown_until - os.time()
        vipzhyla.announce(spell.name .. " estara listo en " .. remaining .. " segundos")
        return false
    end

    -- Check mana
    if not M.drain_mana(spell.cost) then
        vipzhyla.announce("Mana insuficiente para " .. spell.name .. " (necesitas " .. spell.cost .. ")")
        return false
    end

    -- Cast spell
    local cmd = "lanzo " .. spell_name
    if target then
        cmd = cmd .. " " .. target
    end
    vipzhyla.send_command(cmd)

    -- Set cooldown
    magic_state.spell_cooldowns[spell_name] = os.time() + spell.cooldown

    vipzhyla.announce("Lanzando: " .. spell.name)
    return true
end

function M.can_cast_spell(spell_name)
    --[[Check if spell can be cast right now.]]
    local spell = SPELLS[spell_name]
    if not spell then return false end

    if not known_spells[spell_name] then return false end
    if not spell.castable then return false end

    -- Check cooldown
    local cooldown_until = magic_state.spell_cooldowns[spell_name]
    if cooldown_until and os.time() < cooldown_until then
        return false
    end

    -- Check mana
    return M.is_mana_available(spell.cost)
end

--[[ ===== Spell Cooldown Management ===== ]]

function M.get_spell_cooldown(spell_name)
    --[[Get remaining cooldown in seconds.]]
    local cooldown_until = magic_state.spell_cooldowns[spell_name]
    if not cooldown_until then
        return 0
    end

    local remaining = cooldown_until - os.time()
    return math.max(0, remaining)
end

function M.is_spell_ready(spell_name)
    --[[Check if spell cooldown expired.]]
    return M.get_spell_cooldown(spell_name) == 0
end

function M.update_cooldowns()
    --[[Remove expired cooldowns (call periodically).]]
    local now = os.time()
    for spell_name, until_time in pairs(magic_state.spell_cooldowns) do
        if now >= until_time then
            magic_state.spell_cooldowns[spell_name] = nil
        end
    end
end

--[[ ===== Spell Management ===== ]]

function M.learn_spell(spell_name)
    --[[Unlock a spell.]]
    if not SPELLS[spell_name] then
        return false
    end
    known_spells[spell_name] = true
    vipzhyla.announce("Aprendiste: " .. SPELLS[spell_name].name)
    return true
end

function M.forget_spell(spell_name)
    --[[Forget a learned spell.]]
    known_spells[spell_name] = nil
    vipzhyla.announce("Olvidaste: " .. SPELLS[spell_name].name)
    return true
end

function M.has_spell(spell_name)
    --[[Check if spell is known.]]
    return known_spells[spell_name] ~= nil
end

function M.get_known_spells()
    --[[Return table of known spell names.]]
    local spells = {}
    for spell_name, _ in pairs(known_spells) do
        table.insert(spells, spell_name)
    end
    return spells
end

function M.get_spells_by_school(school_name)
    --[[Get all known spells in a school.]]
    local spells = {}
    for spell_name, known in pairs(known_spells) do
        if known then
            local spell = SPELLS[spell_name]
            if spell and spell.school == school_name then
                table.insert(spells, spell)
            end
        end
    end
    return spells
end

function M.get_spell_info(spell_name)
    --[[Get spell details.]]
    return SPELLS[spell_name]
end

--[[ ===== Pattern Detection ===== ]]

function M.detect_spell_cast(text)
    --[[
    Detect spell cast from MUD message.

    Returns:
        Spell name if detected, nil otherwise
    ]]

    for spell_name, patterns in pairs(SPELL_PATTERNS) do
        for _, pattern in ipairs(patterns) do
            if string.find(text:lower(), pattern:lower(), 1, true) then
                return spell_name
            end
        end
    end
    return nil
end

function M.process_message(text)
    --[[
    Auto-detect spell casts from MUD message.
    Called from game.on_mud_message().
    ]]

    local spell = M.detect_spell_cast(text)
    if spell then
        vipzhyla.announce("Hechizo detectado: " .. spell)
        return spell
    end

    return nil
end

--[[ ===== Mana Regeneration ===== ]]

function M.update_mana_regen()
    --[[
    Update mana regeneration (call periodically from main loop).
    ]]

    local now = os.time()
    local elapsed = now - magic_state.last_mana_regen

    if elapsed >= 1 then
        -- Regenerate mana
        local regen_amount = magic_state.mana_regen * elapsed
        if magic_state.mana < magic_state.max_mana then
            magic_state.mana = math.min(
                magic_state.mana + regen_amount,
                magic_state.max_mana
            )
        end
        magic_state.last_mana_regen = now
    end
end

function M.set_mana_regen(amount)
    --[[Set mana regeneration rate (per second).]]
    magic_state.mana_regen = amount
end

--[[ ===== Status Display ===== ]]

function M.format_magic_status()
    --[[Return formatted magic status string.]]
    local lines = {}
    table.insert(lines, "=== MAGIA ===")

    local mana_bar = math.floor(magic_state.mana / magic_state.max_mana * 20)
    local mana_str = string.rep("=", mana_bar) .. string.rep("-", 20 - mana_bar)

    table.insert(lines, string.format(
        "Mana: %d / %d (%.0f%%)\n[%s]",
        magic_state.mana,
        magic_state.max_mana,
        M.get_mana_percent(),
        mana_str
    ))

    table.insert(lines, "")
    table.insert(lines, "Hechizos listos:")

    local ready_count = 0
    for spell_name, known in pairs(known_spells) do
        if known and M.can_cast_spell(spell_name) then
            table.insert(lines, "  - " .. SPELLS[spell_name].name)
            ready_count = ready_count + 1
        end
    end

    if ready_count == 0 then
        table.insert(lines, "  (ninguno disponible)")
    end

    return table.concat(lines, "\n")
end

--[[ ===== Testing/Reset ===== ]]

function M.clear_spells()
    --[[Clear all known spells (for testing).]]
    known_spells = {}
    vipzhyla.announce("Hechizos olvidados")
end

function M.get_magic_state()
    --[[Return raw magic state.]]
    return {
        mana = magic_state.mana,
        max_mana = magic_state.max_mana,
        mana_regen = magic_state.mana_regen,
    }
end

return M

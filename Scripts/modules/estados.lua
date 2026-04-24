--[[
Estados/Buffs System - Status Effects and Condition Tracking

Manages buffs, debuffs, status effects with duration, stacking logic,
and integration with combat system.

Phase 7A: Complete game state management
]]

local M = {}

-- Status effect database
local STATUS_EFFECTS = {
    -- Positive buffs
    haste = {
        name = "Haste",
        type = "buff",
        duration = 300,  -- seconds
        stackable = false,
        description = "Increased movement speed"
    },
    strength = {
        name = "Strength Buff",
        type = "buff",
        duration = 600,
        stackable = false,
        description = "+2 Strength"
    },
    shield = {
        name = "Shield",
        type = "buff",
        duration = 300,
        stackable = false,
        description = "Protective barrier"
    },
    clarity = {
        name = "Mental Clarity",
        type = "buff",
        duration = 300,
        stackable = false,
        description = "Enhanced focus"
    },
    regeneration = {
        name = "Regeneration",
        type = "buff",
        duration = 600,
        stackable = true,
        max_stacks = 3,
        description = "Heal over time"
    },

    -- Negative debuffs
    poison = {
        name = "Poison",
        type = "debuff",
        duration = 300,
        stackable = true,
        max_stacks = 5,
        description = "Taking damage over time"
    },
    curse = {
        name = "Curse",
        type = "debuff",
        duration = 600,
        stackable = false,
        description = "Reduced effectiveness"
    },
    slow = {
        name = "Slow",
        type = "debuff",
        duration = 300,
        stackable = false,
        description = "Movement speed reduced"
    },
    blind = {
        name = "Blindness",
        type = "debuff",
        duration = 180,
        stackable = false,
        description = "Cannot see"
    },
    stun = {
        name = "Stun",
        type = "debuff",
        duration = 30,
        stackable = false,
        description = "Immobilized"
    },
    paralysis = {
        name = "Paralysis",
        type = "debuff",
        duration = 120,
        stackable = false,
        description = "Cannot move or attack"
    },
    weakness = {
        name = "Weakness",
        type = "debuff",
        duration = 300,
        stackable = true,
        max_stacks = 3,
        description = "-1 to all damage"
    },
}

-- Pattern detection for status effects
local BUFF_PATTERNS = {
    haste = {
        "Sientes que tu cuerpo se llena de energía",
        "Tu velocidad aumenta",
        "aura roja",
    },
    strength = {
        "Sientes un aumento de fuerza",
        "Te sientes más fuerte",
        "Tu fuerza se incrementa",
    },
    shield = {
        "Un escudo protector te envuelve",
        "Te rodea una barrera",
        "protección mágica",
    },
    clarity = {
        "Tu mente se aclara",
        "clarity",
        "enfoque mental",
    },
    regeneration = {
        "Comienza a brillar con luz dorada",
        "sanación constante",
        "regeneración",
    },
}

local DEBUFF_PATTERNS = {
    poison = {
        "Te envenena",
        "inyecta veneno",
        "purple aura",
        "tóxico",
    },
    curse = {
        "Te maldice",
        "curse descends",
        "maldición",
    },
    slow = {
        "Te ralentiza",
        "moving slowly",
        "ralentecimiento",
    },
    blind = {
        "Quedas ciego",
        "vision fades",
        "ceguera",
    },
    stun = {
        "Te aturdís",
        "stunned",
        "aturdimiento",
    },
    paralysis = {
        "Te paraliza",
        "paralyzed",
        "parálisis",
    },
    weakness = {
        "Te debilita",
        "weakened",
        "debilitamiento",
    },
}

-- Current active status effects on player
local active_effects = {}

-- Expiration tracking
local effect_timers = {}

function M.init(game)
    game.estados = game.estados or {}
    game.estados.effects = active_effects
    game.estados.database = STATUS_EFFECTS
end

--[[ ===== Core Status Management ===== ]]

function M.add_effect(effect_name, duration)
    [[
    Add a status effect with optional duration override.

    Args:
        effect_name: Name of effect (e.g., "haste", "poison")
        duration: Optional duration override (seconds)

    Returns:
        true if added successfully
    ]]

    local effect_def = STATUS_EFFECTS[effect_name]
    if not effect_def then
        return false
    end

    local actual_duration = duration or effect_def.duration

    if not effect_def.stackable then
        -- Non-stackable: replace if exists
        if active_effects[effect_name] then
            M.remove_effect(effect_name)
        end
        active_effects[effect_name] = {
            name = effect_def.name,
            type = effect_def.type,
            start_time = os.time(),
            duration = actual_duration,
            stacks = 1,
        }
    else
        -- Stackable: increment stacks
        if not active_effects[effect_name] then
            active_effects[effect_name] = {
                name = effect_def.name,
                type = effect_def.type,
                start_time = os.time(),
                duration = actual_duration,
                stacks = 1,
            }
        else
            local max_stacks = effect_def.max_stacks or 999
            if active_effects[effect_name].stacks < max_stacks then
                active_effects[effect_name].stacks = active_effects[effect_name].stacks + 1
                -- Reset duration on new stack
                active_effects[effect_name].start_time = os.time()
            end
        end
    end

    -- Announce
    local effect = active_effects[effect_name]
    local msg = effect.name
    if effect.stacks > 1 then
        msg = msg .. " (x" .. effect.stacks .. ")"
    end

    if effect.type == "buff" then
        vipzhyla.announce("Buff: " .. msg)
    else
        vipzhyla.announce("Debuff: " .. msg)
    end

    return true
end

function M.remove_effect(effect_name)
    [[Remove a status effect.]]

    if active_effects[effect_name] then
        local effect = active_effects[effect_name]
        vipzhyla.announce("Effect ended: " .. effect.name)
        active_effects[effect_name] = nil
        return true
    end
    return false
end

function M.has_effect(effect_name)
    [[Check if effect is currently active.]]
    return active_effects[effect_name] ~= nil
end

function M.get_effect(effect_name)
    [[Get effect details if active.]]
    return active_effects[effect_name]
end

--[[ ===== Effect Status Queries ===== ]]

function M.get_active_buffs()
    [[Return table of all active buffs.]]
    local buffs = {}
    for name, effect in pairs(active_effects) do
        if effect.type == "buff" then
            table.insert(buffs, effect)
        end
    end
    return buffs
end

function M.get_active_debuffs()
    [[Return table of all active debuffs.]]
    local debuffs = {}
    for name, effect in pairs(active_effects) do
        if effect.type == "debuff" then
            table.insert(debuffs, effect)
        end
    end
    return debuffs
end

function M.count_buffs()
    [[Count total active buffs.]]
    return #M.get_active_buffs()
end

function M.count_debuffs()
    [[Count total active debuffs.]]
    return #M.get_active_debuffs()
end

function M.is_under_effect(effect_name)
    [[Check if player is under specific effect.]]
    return M.has_effect(effect_name)
end

--[[ ===== Duration Management ===== ]]

function M.update_durations()
    [[
    Update effect durations (call periodically from main loop).
    Remove expired effects.
    ]]

    local current_time = os.time()
    local expired = {}

    for effect_name, effect in pairs(active_effects) do
        local elapsed = current_time - effect.start_time
        if elapsed >= effect.duration then
            table.insert(expired, effect_name)
        end
    end

    -- Remove expired effects
    for _, effect_name in ipairs(expired) do
        M.remove_effect(effect_name)
    end
end

function M.get_remaining_duration(effect_name)
    [[Get seconds remaining on effect.]]

    local effect = active_effects[effect_name]
    if not effect then
        return nil
    end

    local elapsed = os.time() - effect.start_time
    local remaining = effect.duration - elapsed
    return math.max(0, remaining)
end

function M.extend_effect(effect_name, extra_seconds)
    [[Extend duration of active effect.]]

    if not active_effects[effect_name] then
        return false
    end

    active_effects[effect_name].duration = active_effects[effect_name].duration + extra_seconds
    vipzhyla.announce("Effect extended: " .. active_effects[effect_name].name)
    return true
end

--[[ ===== Pattern Detection ===== ]]

function M.detect_buff(text)
    [[
    Detect buff effect from MUD message.

    Args:
        text: MUD message text

    Returns:
        Effect name if detected, nil otherwise
    ]]

    for effect_name, patterns in pairs(BUFF_PATTERNS) do
        for _, pattern in ipairs(patterns) do
            if string.find(text:lower(), pattern:lower(), 1, true) then
                return effect_name
            end
        end
    end
    return nil
end

function M.detect_debuff(text)
    [[
    Detect debuff effect from MUD message.

    Args:
        text: MUD message text

    Returns:
        Effect name if detected, nil otherwise
    ]]

    for effect_name, patterns in pairs(DEBUFF_PATTERNS) do
        for _, pattern in ipairs(patterns) do
            if string.find(text:lower(), pattern:lower(), 1, true) then
                return effect_name
            end
        end
    end
    return nil
end

function M.process_message(text)
    [[
    Auto-detect buffs/debuffs from MUD message.
    Called by trigger system automatically.
    ]]

    local buff = M.detect_buff(text)
    if buff then
        M.add_effect(buff)
        return "buff"
    end

    local debuff = M.detect_debuff(text)
    if debuff then
        M.add_effect(debuff)
        return "debuff"
    end

    return nil
end

--[[ ===== Expiration Patterns ===== ]]

function M.detect_effect_expiration(text)
    [[
    Detect when an effect expires from MUD message.

    Returns:
        Effect name if expiration detected, nil otherwise
    ]]

    local patterns = {
        "desaparece",
        "effect ended",
        "ya no",
        "se disipa",
    }

    for _, pattern in ipairs(patterns) do
        if string.find(text:lower(), pattern:lower(), 1, true) then
            -- Try to extract effect name from message
            -- For now, just return generic expiration
            return "unknown"
        end
    end

    return nil
end

--[[ ===== Combat Integration ===== ]]

function M.get_combat_modifiers()
    [[
    Get total combat modifiers from active effects.

    Returns:
        Table with modifier values for damage, defense, etc.
    ]]

    local mods = {
        damage = 0,
        defense = 0,
        speed = 0,
        accuracy = 0,
    }

    for effect_name, effect in pairs(active_effects) do
        if effect_name == "strength" and effect.type == "buff" then
            mods.damage = mods.damage + 2
        elseif effect_name == "weakness" and effect.type == "debuff" then
            mods.damage = mods.damage - 1 * effect.stacks
        elseif effect_name == "shield" and effect.type == "buff" then
            mods.defense = mods.defense + 2
        elseif effect_name == "haste" and effect.type == "buff" then
            mods.speed = mods.speed + 1
        elseif effect_name == "slow" and effect.type == "debuff" then
            mods.speed = mods.speed - 1
        elseif effect_name == "blind" and effect.type == "debuff" then
            mods.accuracy = mods.accuracy - 3
        elseif effect_name == "clarity" and effect.type == "buff" then
            mods.accuracy = mods.accuracy + 2
        end
    end

    return mods
end

--[[ ===== Clear All (for testing/reset) ===== ]]

function M.clear_all_effects()
    [[Clear all active effects (usually for testing).]]
    active_effects = {}
    vipzhyla.announce("All effects cleared")
end

function M.get_all_effects()
    [[Return table of all active effects for UI display.]]
    return active_effects
end

return M

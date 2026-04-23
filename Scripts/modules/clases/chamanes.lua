--[[
Chamanes (Shaman) Class Module

Shamans are spellcasters who communicate with spirits.
They specialize in:
- Fire/Lightning magic
- Healing and buffs
- Summoning spirits
- Totems and ground effects

Abilities based on: VipMud Chamanes.set (301 lines, 70 triggers)
]]

local ClassBase = require("modules.clases.base")
local M = {}

-- Create Shaman class
local Shaman = ClassBase.new("Chamán")

-- Add class-specific bonuses
Shaman:add_passive_bonus("intelligence", 2)
Shaman:add_passive_bonus("wisdom", 1)

-- Add Shaman abilities
Shaman:add_ability("Shock", "Descarga de electricidad", "spell")
Shaman:add_ability("Fireball", "Bola de fuego", "spell")
Shaman:add_ability("Healing Wave", "Onda de curación", "heal")
Shaman:add_ability("Totem of Fire", "Tótem de fuego", "summon")
Shaman:add_ability("Totem of Ice", "Tótem de hielo", "summon")
Shaman:add_ability("Spirit Walk", "Caminar espiritual", "buff")
Shaman:add_ability("Chain Lightning", "Relámpago en cadena", "spell")
Shaman:add_ability("Bloodlust", "Sed de sangre", "buff")
Shaman:add_ability("Earthbind", "Atadura terrestre", "control")

-- Module initialization
function M.init(game)
    vipzhyla.say("[CHAMANES] Habilidades del Chamán cargadas")
end

-- Get Shaman class definition
function M.get_class()
    return Shaman
end

-- Get Shaman abilities
function M.get_abilities()
    return Shaman:get_abilities()
end

-- Handle Shaman-specific combat patterns
function M.detect_ability(text)
    local text_lower = text:lower()

    -- Shaman-specific patterns
    if text_lower:match("descarga") then
        return { name = "Shock", type = "spell", damage_type = "lightning" }
    elseif text_lower:match("bola de fuego") then
        return { name = "Fireball", type = "spell", damage_type = "fire" }
    elseif text_lower:match("onda") then
        return { name = "Healing Wave", type = "heal" }
    elseif text_lower:match("totem") then
        return { name = "Totem", type = "summon" }
    elseif text_lower:match("espiritual") then
        return { name = "Spirit Walk", type = "buff" }
    elseif text_lower:match("relampago") then
        return { name = "Chain Lightning", type = "spell", damage_type = "lightning" }
    elseif text_lower:match("sed de sangre") then
        return { name = "Bloodlust", type = "buff" }
    elseif text_lower:match("atadura") then
        return { name = "Earthbind", type = "control" }
    end

    return nil
end

return M

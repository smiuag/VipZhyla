--[[
Paladines (Paladin) Class Module

Paladins are holy warriors combining combat with divine magic.
They specialize in:
- Melee combat with divine weapons
- Healing and protection spells
- Buffs and party support
- Undead detection and turning

Abilities based on: VipMud Paladines.set (320 lines, 80 triggers)
]]

local ClassBase = require("modules.clases.base")
local M = {}

-- Create Paladin class
local Paladin = ClassBase.new("Paladín")

-- Add class-specific bonuses
Paladin:add_passive_bonus("strength", 1)
Paladin:add_passive_bonus("intelligence", 1)
Paladin:add_passive_bonus("wisdom", 2)

-- Add Paladin abilities
Paladin:add_ability("Holy Strike", "Golpe sagrado", "physical")
Paladin:add_ability("Divine Shield", "Escudo divino", "buff")
Paladin:add_ability("Healing Light", "Luz sanadora", "heal")
Paladin:add_ability("Holy Armor", "Armadura sagrada", "buff")
Paladin:add_ability("Righteous Fury", "Furia justa", "buff")
Paladin:add_ability("Consecration", "Consagración", "area")
Paladin:add_ability("Turn Undead", "Repeler no-muertos", "control")
Paladin:add_ability("Divine Punishment", "Castigo divino", "spell")
Paladin:add_ability("Aura of Protection", "Aura de protección", "buff")
Paladin:add_ability("Holy Wrath", "Ira divina", "spell")

-- Module initialization
function M.init(game)
    vipzhyla.say("[PALADINES] Habilidades del Paladín cargadas")
end

-- Get Paladin class definition
function M.get_class()
    return Paladin
end

-- Get Paladin abilities
function M.get_abilities()
    return Paladin:get_abilities()
end

-- Handle Paladin-specific combat patterns
function M.detect_ability(text)
    local text_lower = text:lower()

    if text_lower:match("golpe sagrado") then
        return { name = "Holy Strike", type = "physical" }
    elseif text_lower:match("escudo divino") then
        return { name = "Divine Shield", type = "buff" }
    elseif text_lower:match("luz sanadora") then
        return { name = "Healing Light", type = "heal" }
    elseif text_lower:match("armadura sagrada") then
        return { name = "Holy Armor", type = "buff" }
    elseif text_lower:match("furia justa") then
        return { name = "Righteous Fury", type = "buff" }
    elseif text_lower:match("consagración") then
        return { name = "Consecration", type = "area" }
    elseif text_lower:match("no.muerto") then
        return { name = "Turn Undead", type = "control" }
    elseif text_lower:match("castigo divino") then
        return { name = "Divine Punishment", type = "spell" }
    elseif text_lower:match("aura") then
        return { name = "Aura of Protection", type = "buff" }
    elseif text_lower:match("ira divina") then
        return { name = "Holy Wrath", type = "spell" }
    end

    return nil
end

return M

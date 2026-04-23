--[[
Khazads (Dwarf) Class Module

Dwarves are stout warriors known for their mining, smithing, and combat prowess.
They specialize in:
- Melee combat (axes, hammers)
- Mining and smithing
- Defensive techniques
- Stone magic

Abilities based on: VipMud Khazads.set (310 lines, 75 triggers)
]]

local ClassBase = require("modules.clases.base")
local M = {}

-- Create Khazad class
local Khazad = ClassBase.new("Khazad")

-- Add class-specific bonuses (dwarves are tough and strong)
Khazad:add_passive_bonus("strength", 2)
Khazad:add_passive_bonus("constitution", 2)

-- Add Khazad abilities
Khazad:add_ability("Axe Slash", "Tajo de hacha", "physical")
Khazad:add_ability("Shield Bash", "Golpe de escudo", "physical")
Khazad:add_ability("Stone Skin", "Piel de piedra", "buff")
Khazad:add_ability("War Cry", "Grito de guerra", "buff")
Khazad:add_ability("Hammer Blow", "Golpe de martillo", "physical")
Khazad:add_ability("Mining", "Minería", "special")
Khazad:add_ability("Stone Fist", "Puño de piedra", "physical")
Khazad:add_ability("Fortress", "Fortaleza", "buff")
Khazad:add_ability("Ancestral Strength", "Fuerza ancestral", "buff")

-- Module initialization
function M.init(game)
    vipzhyla.say("[KHAZADS] Habilidades del Khazad cargadas")
end

-- Get Khazad class definition
function M.get_class()
    return Khazad
end

-- Get Khazad abilities
function M.get_abilities()
    return Khazad:get_abilities()
end

-- Handle Khazad-specific combat patterns
function M.detect_ability(text)
    local text_lower = text:lower()

    if text_lower:match("tajo") or text_lower:match("hacha") then
        return { name = "Axe Slash", type = "physical" }
    elseif text_lower:match("golpe de escudo") then
        return { name = "Shield Bash", type = "physical" }
    elseif text_lower:match("piel de piedra") then
        return { name = "Stone Skin", type = "buff" }
    elseif text_lower:match("grito de guerra") then
        return { name = "War Cry", type = "buff" }
    elseif text_lower:match("martillo") then
        return { name = "Hammer Blow", type = "physical" }
    elseif text_lower:match("mina") or text_lower:match("minería") then
        return { name = "Mining", type = "special" }
    elseif text_lower:match("puño de piedra") then
        return { name = "Stone Fist", type = "physical" }
    elseif text_lower:match("fortaleza") then
        return { name = "Fortress", type = "buff" }
    elseif text_lower:match("fuerza ancestral") then
        return { name = "Ancestral Strength", type = "buff" }
    end

    return nil
end

return M

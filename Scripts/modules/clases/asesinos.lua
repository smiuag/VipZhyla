--[[
Asesinos (Assassin) Class Module
Stealth, high damage, critical strikes.
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Assassin = ClassBase.new("Asesino")
Assassin:add_passive_bonus("dexterity", 3)
Assassin:add_passive_bonus("intelligence", 1)

Assassin:add_ability("Backstab", "Apuñaladura", "physical")
Assassin:add_ability("Poison", "Veneno", "debuff")
Assassin:add_ability("Stealth", "Sigilo", "buff")
Assassin:add_ability("Shadow Clone", "Clon de sombra", "summon")
Assassin:add_ability("Smoke Bomb", "Bomba de humo", "special")
Assassin:add_ability("Assassination", "Asesinato", "physical")
Assassin:add_ability("Evasion", "Evasión", "buff")
Assassin:add_ability("Poison Dart", "Dardo envenenado", "physical")
Assassin:add_ability("Ambush", "Emboscada", "physical")

function M.init(game)
    vipzhyla.say("[ASESINOS] Habilidades del Asesino cargadas")
end

function M.get_class()
    return Assassin
end

function M.get_abilities()
    return Assassin:get_abilities()
end

function M.detect_ability(text)
    local text_lower = text:lower()
    if text_lower:match("apuñaladura") then
        return { name = "Backstab", type = "physical" }
    elseif text_lower:match("veneno") then
        return { name = "Poison", type = "debuff" }
    elseif text_lower:match("sigilo") then
        return { name = "Stealth", type = "buff" }
    elseif text_lower:match("sombra") then
        return { name = "Shadow Clone", type = "summon" }
    elseif text_lower:match("humo") then
        return { name = "Smoke Bomb", type = "special" }
    elseif text_lower:match("asesinato") then
        return { name = "Assassination", type = "physical" }
    elseif text_lower:match("evasión") then
        return { name = "Evasion", type = "buff" }
    elseif text_lower:match("dardo") then
        return { name = "Poison Dart", type = "physical" }
    elseif text_lower:match("emboscada") then
        return { name = "Ambush", type = "physical" }
    end
    return nil
end

return M

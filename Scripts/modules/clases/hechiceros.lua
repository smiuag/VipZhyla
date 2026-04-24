--[[
Hechiceros (Sorcerer) Class Module
Innate arcane casters specializing in dark magic, demonic summons, and
life-drain spells.
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Sorcerer = ClassBase.new("Hechicero")
Sorcerer:add_passive_bonus("intelligence", 3)

for _, a in ipairs({
    "Curse", "Summon Demon", "Dark Bolt", "Drain",
    "Hellfire", "Sacrifice", "Corruption", "Infernal Shield"
}) do
    Sorcerer:add_ability(a, a, "spell")
end

function M.init(game) vipzhyla.say("[HECHICEROS] Hechicero cargado") end
function M.get_class() return Sorcerer end
function M.get_abilities() return Sorcerer:get_abilities() end

function M.detect_ability(text)
    if not text then return nil end
    local t = text:lower()
    if t:match("maldición") or t:match("curse") then
        return { name = "Curse", type = "debuff" }
    elseif t:match("invocas? un demonio") or t:match("summon demon") then
        return { name = "Summon Demon", type = "summon" }
    elseif t:match("rayo oscuro") or t:match("dark bolt") then
        return { name = "Dark Bolt", type = "spell" }
    elseif t:match("drenaje") or t:match("drain") then
        return { name = "Drain", type = "spell" }
    elseif t:match("fuego infernal") or t:match("hellfire") then
        return { name = "Hellfire", type = "area" }
    elseif t:match("sacrificio") or t:match("sacrifice") then
        return { name = "Sacrifice", type = "special" }
    elseif t:match("corrupción") or t:match("corruption") then
        return { name = "Corruption", type = "debuff" }
    elseif t:match("escudo infernal") or t:match("infernal shield") then
        return { name = "Infernal Shield", type = "buff" }
    end
    return nil
end

return M

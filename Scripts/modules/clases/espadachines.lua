--[[
Espadachines (Swordmasters) Class Module
Disciplined sword duelists. Precision strikes, parries, and chained
combo attacks.
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Swordmaster = ClassBase.new("Espadachín")
Swordmaster:add_passive_bonus("strength", 2)
Swordmaster:add_passive_bonus("dexterity", 2)

for _, a in ipairs({"Sword Mastery", "Precision", "Riposte", "Parry", "Combo"}) do
    Swordmaster:add_ability(a, a, "physical")
end

function M.init(game) vipzhyla.say("[ESPADACHINES] Espadachín cargado") end
function M.get_class() return Swordmaster end
function M.get_abilities() return Swordmaster:get_abilities() end

function M.detect_ability(text)
    if not text then return nil end
    local t = text:lower()
    if t:match("maestría") or t:match("sword mastery") then
        return { name = "Sword Mastery", type = "buff" }
    elseif t:match("precisión") or t:match("precision") then
        return { name = "Precision", type = "buff" }
    elseif t:match("contragolpe") or t:match("riposte") then
        return { name = "Riposte", type = "physical" }
    elseif t:match("parada") or t:match("parry") then
        return { name = "Parry", type = "buff" }
    elseif t:match("combo") then
        return { name = "Combo", type = "physical" }
    end
    return nil
end

return M

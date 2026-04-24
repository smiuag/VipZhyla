--[[
Alquimistas (Alchemist) Class Module
Crafters of potions and explosives. Mixes utility throws with healing
elixirs and offensive concoctions.
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Alchemist = ClassBase.new("Alquimista")
Alchemist:add_passive_bonus("intelligence", 2)

for _, a in ipairs({"Transmute", "Throw Potion", "Acid", "Explosive", "Heal Potion", "Buff Potion"}) do
    Alchemist:add_ability(a, a, "spell")
end

function M.init(game) vipzhyla.say("[ALQUIMISTAS] Alquimista cargado") end
function M.get_class() return Alchemist end
function M.get_abilities() return Alchemist:get_abilities() end

function M.detect_ability(text)
    if not text then return nil end
    local t = text:lower()
    if t:match("transmuta") then
        return { name = "Transmute", type = "special" }
    elseif t:match("lanzas? una poción") or t:match("throw potion") then
        return { name = "Throw Potion", type = "spell" }
    elseif t:match("ácido") or t:match("acid") then
        return { name = "Acid", type = "debuff" }
    elseif t:match("explosiv") then
        return { name = "Explosive", type = "area" }
    elseif t:match("poción de curación") or t:match("heal potion") then
        return { name = "Heal Potion", type = "heal" }
    elseif t:match("poción de mejora") or t:match("buff potion") then
        return { name = "Buff Potion", type = "buff" }
    end
    return nil
end

return M

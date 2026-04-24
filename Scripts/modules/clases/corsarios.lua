--[[
Corsarios (Corsairs) Class Module
Pirate-style duelists. Cutlass, pistol, plunder and slippery escapes.
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Corsair = ClassBase.new("Corsario")
Corsair:add_passive_bonus("dexterity", 2)
Corsair:add_passive_bonus("strength", 1)

for _, a in ipairs({"Cutlass", "Pistol Shot", "Plunder", "Evasion", "Swashbuckle"}) do
    Corsair:add_ability(a, a, "physical")
end

function M.init(game) vipzhyla.say("[CORSARIOS] Corsario cargado") end
function M.get_class() return Corsair end
function M.get_abilities() return Corsair:get_abilities() end

function M.detect_ability(text)
    if not text then return nil end
    local t = text:lower()
    if t:match("sable") or t:match("cutlass") then
        return { name = "Cutlass", type = "physical" }
    elseif t:match("pistola") or t:match("pistol shot") then
        return { name = "Pistol Shot", type = "physical" }
    elseif t:match("saquea") or t:match("plunder") then
        return { name = "Plunder", type = "special" }
    elseif t:match("evasión") or t:match("evasion") then
        return { name = "Evasion", type = "buff" }
    elseif t:match("alarde") or t:match("swashbuckle") then
        return { name = "Swashbuckle", type = "buff" }
    end
    return nil
end

return M

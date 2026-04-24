--[[
Trovadores (Troubadors) Class Module
Charismatic performers. Songs that buff allies, charm crowds, and
distract foes.
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Troubador = ClassBase.new("Trovador")
Troubador:add_passive_bonus("charisma", 3)
Troubador:add_passive_bonus("dexterity", 1)

for _, a in ipairs({"Sing", "Inspire", "Entertain", "Charm", "Performance"}) do
    Troubador:add_ability(a, a, "buff")
end

function M.init(game) vipzhyla.say("[TROVADORES] Trovador cargado") end
function M.get_class() return Troubador end
function M.get_abilities() return Troubador:get_abilities() end

function M.detect_ability(text)
    if not text then return nil end
    local t = text:lower()
    if t:match("canta") or t:match("sing") then
        return { name = "Sing", type = "buff" }
    elseif t:match("inspira") or t:match("inspire") then
        return { name = "Inspire", type = "buff" }
    elseif t:match("entreten") or t:match("entertain") then
        return { name = "Entertain", type = "buff" }
    elseif t:match("encanto") or t:match("charm") then
        return { name = "Charm", type = "control" }
    elseif t:match("actuación") or t:match("performance") then
        return { name = "Performance", type = "buff" }
    end
    return nil
end

return M

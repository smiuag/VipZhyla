local ClassBase = require("modules.clases.base")
local M = {}
local Troubador = ClassBase.new("Trovador")
Troubador:add_passive_bonus("charisma", 3)
Troubador:add_passive_bonus("dexterity", 1)
for _, a in ipairs({"Sing", "Inspire", "Entertain", "Charm", "Performance"}) do
    Troubador:add_ability(a, a, "buff")
end
function M.init(game) end
function M.get_class() return Troubador end
function M.get_abilities() return Troubador:get_abilities() end
function M.detect_ability(text) return nil end
return M

local ClassBase = require("modules.clases.base")
local M = {}
local Corsair = ClassBase.new("Corsario")
Corsair:add_passive_bonus("dexterity", 2)
Corsair:add_passive_bonus("strength", 1)
for _, a in ipairs({"Cutlass", "Pistol Shot", "Plunder", "Evasion", "Swashbuckle"}) do
    Corsair:add_ability(a, a, "physical")
end
function M.init(game) end
function M.get_class() return Corsair end
function M.get_abilities() return Corsair:get_abilities() end
function M.detect_ability(text) return nil end
return M

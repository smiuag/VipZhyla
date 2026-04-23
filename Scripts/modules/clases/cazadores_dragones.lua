local ClassBase = require("modules.clases.base")
local M = {}
local SlayerC = ClassBase.new("Cazador_de_Dragones")
SlayerC:add_passive_bonus("strength", 2)
SlayerC:add_passive_bonus("intelligence", 1)
for _, a in ipairs({"Dragon Slash", "Scales", "Dragon Breath", "Fire Resistance", "Dragon Hunt"}) do
    SlayerC:add_ability(a, a, "physical")
end
function M.init(game) end
function M.get_class() return SlayerC end
function M.get_abilities() return SlayerC:get_abilities() end
function M.detect_ability(text) return nil end
return M

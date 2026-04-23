local ClassBase = require("modules.clases.base")
local M = {}
local Witch = ClassBase.new("Brujo")
Witch:add_passive_bonus("intelligence", 2)
Witch:add_passive_bonus("wisdom", 2)
for _, a in ipairs({"Hex", "Potion", "Spell Steal", "Blight", "Ward", "Enchant"}) do
    Witch:add_ability(a, a, "spell")
end
function M.init(game) end
function M.get_class() return Witch end
function M.get_abilities() return Witch:get_abilities() end
function M.detect_ability(text) return nil end
return M

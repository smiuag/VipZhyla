local ClassBase = require("modules.clases.base")
local M = {}
local Alchemist = ClassBase.new("Alquimista")
Alchemist:add_passive_bonus("intelligence", 2)
for _, a in ipairs({"Transmute", "Throw Potion", "Acid", "Explosive", "Heal Potion", "Buff Potion"}) do
    Alchemist:add_ability(a, a, "spell")
end
function M.init(game) end
function M.get_class() return Alchemist end
function M.get_abilities() return Alchemist:get_abilities() end
function M.detect_ability(text) return nil end
return M

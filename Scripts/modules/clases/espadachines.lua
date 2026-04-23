local ClassBase = require("modules.clases.base")
local M = {}
local Swordmaster = ClassBase.new("Espadachín")
Swordmaster:add_passive_bonus("strength", 2)
Swordmaster:add_passive_bonus("dexterity", 2)
for _, a in ipairs({"Sword Mastery", "Precision", "Riposte", "Parry", "Combo"}) do
    Swordmaster:add_ability(a, a, "physical")
end
function M.init(game) end
function M.get_class() return Swordmaster end
function M.get_abilities() return Swordmaster:get_abilities() end
function M.detect_ability(text) return nil end
return M

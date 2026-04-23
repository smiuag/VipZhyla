local ClassBase = require("modules.clases.base")
local M = {}
local Warlock = ClassBase.new("Hechicero")
Warlock:add_passive_bonus("intelligence", 3)
for _, a in ipairs({"Curse", "Summon Demon", "Dark Bolt", "Drain", "Hellfire", "Sacrifice", "Corruption", "Infernal Shield"}) do
    Warlock:add_ability(a, a, "spell")
end
function M.init(game) vipzhyla.say("[HECHICEROS] Hechicero cargado") end
function M.get_class() return Warlock end
function M.get_abilities() return Warlock:get_abilities() end
function M.detect_ability(text) return nil end
return M

local ClassBase = require("modules.clases.base")
local M = {}
local DarkKnight = ClassBase.new("Caballero_Oscuro")
DarkKnight:add_passive_bonus("strength", 2)
DarkKnight:add_passive_bonus("intelligence", 1)
for _, a in ipairs({"Dark Strike", "Corruption", "Shadow", "Death Knight", "Dark Aura"}) do
    DarkKnight:add_ability(a, a, "physical")
end
function M.init(game) end
function M.get_class() return DarkKnight end
function M.get_abilities() return DarkKnight:get_abilities() end
function M.detect_ability(text) return nil end
return M

local ClassBase = require("modules.clases.base")
local M = {}

local Templar = ClassBase.new("Templario")
Templar:add_passive_bonus("strength", 2)
Templar:add_passive_bonus("wisdom", 1)
Templar:add_passive_bonus("constitution", 1)

for _, ability in ipairs({"Holy Strike", "Consecration", "Righteous Judgment", "Divine Wrath", "Templar's Wrath", "Holy Shield", "Seal", "Smite", "Avenging Wrath"}) do
    Templar:add_ability(ability, ability, "physical")
end

function M.init(game) vipzhyla.say("[TEMPLARIOS] Templario cargado") end
function M.get_class() return Templar end
function M.get_abilities() return Templar:get_abilities() end
function M.detect_ability(text) return nil end

return M

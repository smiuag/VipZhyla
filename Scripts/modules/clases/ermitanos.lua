local ClassBase = require("modules.clases.base")
local M = {}
local Hermit = ClassBase.new("Ermitaño")
Hermit:add_passive_bonus("wisdom", 3)
for _, a in ipairs({"Meditation", "Inner Strength", "Healing", "Purify", "Transcendence"}) do
    Hermit:add_ability(a, a, "buff")
end
function M.init(game) end
function M.get_class() return Hermit end
function M.get_abilities() return Hermit:get_abilities() end
function M.detect_ability(text) return nil end
return M

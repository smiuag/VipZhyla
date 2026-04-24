--[[
Ermitaños (Hermits) Class Module
Solitary practitioners of self-discipline. Strong on meditation, self-
healing and inner-strength buffs.
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Hermit = ClassBase.new("Ermitaño")
Hermit:add_passive_bonus("wisdom", 3)

for _, a in ipairs({"Meditation", "Inner Strength", "Healing", "Purify", "Transcendence"}) do
    Hermit:add_ability(a, a, "buff")
end

function M.init(game) vipzhyla.say("[ERMITANOS] Ermitaño cargado") end
function M.get_class() return Hermit end
function M.get_abilities() return Hermit:get_abilities() end

function M.detect_ability(text)
    if not text then return nil end
    local t = text:lower()
    if t:match("medita") then
        return { name = "Meditation", type = "buff" }
    elseif t:match("fuerza interior") or t:match("inner strength") then
        return { name = "Inner Strength", type = "buff" }
    elseif t:match("curación") or t:match("healing") or t:match("sanación") then
        return { name = "Healing", type = "heal" }
    elseif t:match("purifica") then
        return { name = "Purify", type = "heal" }
    elseif t:match("trascendencia") or t:match("transcendence") then
        return { name = "Transcendence", type = "special" }
    end
    return nil
end

return M

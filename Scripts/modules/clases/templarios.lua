--[[
Templarios (Templars) Class Module
Holy heavy infantry. Combines paladin-like buffs with anti-undead and
divine wrath spells.
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Templar = ClassBase.new("Templario")
Templar:add_passive_bonus("strength", 2)
Templar:add_passive_bonus("wisdom", 1)
Templar:add_passive_bonus("constitution", 1)

for _, ability in ipairs({
    "Holy Strike", "Consecration", "Righteous Judgment", "Divine Wrath",
    "Templar's Wrath", "Holy Shield", "Seal", "Smite", "Avenging Wrath"
}) do
    Templar:add_ability(ability, ability, "physical")
end

function M.init(game) vipzhyla.say("[TEMPLARIOS] Templario cargado") end
function M.get_class() return Templar end
function M.get_abilities() return Templar:get_abilities() end

function M.detect_ability(text)
    if not text then return nil end
    local t = text:lower()
    if t:match("golpe sagrado") or t:match("holy strike") then
        return { name = "Holy Strike", type = "physical" }
    elseif t:match("consagración") or t:match("consecration") then
        return { name = "Consecration", type = "area" }
    elseif t:match("juicio") or t:match("judgment") then
        return { name = "Righteous Judgment", type = "spell" }
    elseif t:match("ira del templario") or t:match("templar's wrath") then
        return { name = "Templar's Wrath", type = "buff" }
    elseif t:match("ira divina") or t:match("divine wrath") then
        return { name = "Divine Wrath", type = "spell" }
    elseif t:match("escudo sagrado") or t:match("holy shield") then
        return { name = "Holy Shield", type = "buff" }
    elseif t:match("sello") or t:match("seal") then
        return { name = "Seal", type = "buff" }
    elseif t:match("castiga") or t:match("smite") then
        return { name = "Smite", type = "spell" }
    elseif t:match("ira vengadora") or t:match("avenging wrath") then
        return { name = "Avenging Wrath", type = "buff" }
    end
    return nil
end

return M

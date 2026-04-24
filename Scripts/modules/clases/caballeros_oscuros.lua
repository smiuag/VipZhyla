--[[
Caballeros Oscuros (Dark Knights) Class Module
Anti-paladins: heavy melee mixed with corruption-flavoured magic and
shadow auras.
]]

local ClassBase = require("modules.clases.base")
local M = {}

local DarkKnight = ClassBase.new("Caballero_Oscuro")
DarkKnight:add_passive_bonus("strength", 2)
DarkKnight:add_passive_bonus("intelligence", 1)

for _, a in ipairs({"Dark Strike", "Corruption", "Shadow", "Death Knight", "Dark Aura"}) do
    DarkKnight:add_ability(a, a, "physical")
end

function M.init(game) vipzhyla.say("[CABALLEROS_OSCUROS] Caballero Oscuro cargado") end
function M.get_class() return DarkKnight end
function M.get_abilities() return DarkKnight:get_abilities() end

function M.detect_ability(text)
    if not text then return nil end
    local t = text:lower()
    if t:match("golpe oscuro") or t:match("dark strike") then
        return { name = "Dark Strike", type = "physical" }
    elseif t:match("corrupción") or t:match("corruption") then
        return { name = "Corruption", type = "debuff" }
    elseif t:match("sombra") or t:match("shadow") then
        return { name = "Shadow", type = "spell" }
    elseif t:match("caballero de la muerte") or t:match("death knight") then
        return { name = "Death Knight", type = "buff" }
    elseif t:match("aura oscura") or t:match("dark aura") then
        return { name = "Dark Aura", type = "buff" }
    end
    return nil
end

return M

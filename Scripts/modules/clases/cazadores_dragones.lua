--[[
Cazadores de Dragones (Dragon Hunters) Class Module
Specialists in slaying scaled foes. Combines heavy melee with anti-fire
defenses and dragon-tracking utilities.
]]

local ClassBase = require("modules.clases.base")
local M = {}

local DragonHunter = ClassBase.new("Cazador_de_Dragones")
DragonHunter:add_passive_bonus("strength", 2)
DragonHunter:add_passive_bonus("intelligence", 1)

for _, a in ipairs({"Dragon Slash", "Scales", "Dragon Breath", "Fire Resistance", "Dragon Hunt"}) do
    DragonHunter:add_ability(a, a, "physical")
end

function M.init(game) vipzhyla.say("[CAZADORES_DRAGONES] Cazador de Dragones cargado") end
function M.get_class() return DragonHunter end
function M.get_abilities() return DragonHunter:get_abilities() end

function M.detect_ability(text)
    if not text then return nil end
    local t = text:lower()
    if t:match("tajo dragontino") or t:match("dragon slash") then
        return { name = "Dragon Slash", type = "physical" }
    elseif t:match("escamas") or t:match("scales") then
        return { name = "Scales", type = "buff" }
    elseif t:match("aliento de drag") or t:match("dragon breath") then
        return { name = "Dragon Breath", type = "area" }
    elseif t:match("resistencia al fuego") or t:match("fire resistance") then
        return { name = "Fire Resistance", type = "buff" }
    elseif t:match("caza de drag") or t:match("dragon hunt") then
        return { name = "Dragon Hunt", type = "special" }
    end
    return nil
end

return M

local ClassBase = require("modules.clases.base")
local M = {}

local Monk = ClassBase.new("Monje")
Monk:add_passive_bonus("dexterity", 2)
Monk:add_passive_bonus("wisdom", 2)

Monk:add_ability("Kick", "Patada", "physical")
Monk:add_ability("Palm Strike", "Golpe de palma", "physical")
Monk:add_ability("Meditation", "Meditación", "buff")
Monk:add_ability("Inner Peace", "Paz interior", "buff")
Monk:add_ability("Monk Training", "Entrenamiento monástico", "buff")
Monk:add_ability("Flying Kick", "Patada voladora", "area")
Monk:add_ability("Whirlwind Kick", "Patada giratoria", "area")
Monk:add_ability("Heal Self", "Auto-curación", "heal")
Monk:add_ability("Chi Blast", "Ráfaga de chi", "spell")

function M.init(game) vipzhyla.say("[MONJES] Habilidades del Monje cargadas") end
function M.get_class() return Monk end
function M.get_abilities() return Monk:get_abilities() end
function M.detect_ability(text)
    local t = text:lower()
    if t:match("patada voladora") then return { name = "Flying Kick", type = "area" }
    elseif t:match("patada giratoria") then return { name = "Whirlwind Kick", type = "area" }
    elseif t:match("patada") then return { name = "Kick", type = "physical" }
    elseif t:match("golpe de palma") then return { name = "Palm Strike", type = "physical" }
    elseif t:match("meditación") then return { name = "Meditation", type = "buff" }
    elseif t:match("paz interior") then return { name = "Inner Peace", type = "buff" }
    elseif t:match("entrenamiento") then return { name = "Monk Training", type = "buff" }
    elseif t:match("chi") then return { name = "Chi Blast", type = "spell" }
    end
    return nil
end

return M

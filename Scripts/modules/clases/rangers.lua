local ClassBase = require("modules.clases.base")
local M = {}

local Ranger = ClassBase.new("Ranger")
Ranger:add_passive_bonus("dexterity", 2)
Ranger:add_passive_bonus("wisdom", 1)
Ranger:add_passive_bonus("strength", 1)

Ranger:add_ability("Arrow Shot", "Disparo de flecha", "physical")
Ranger:add_ability("Multi Shot", "Disparo múltiple", "area")
Ranger:add_ability("Aimed Shot", "Disparo preciso", "physical")
Ranger:add_ability("Animal Companion", "Compañero animal", "summon")
Ranger:add_ability("Tracking", "Rastreo", "special")
Ranger:add_ability("Camouflage", "Camuflaje", "buff")
Ranger:add_ability("Explosive Arrow", "Flecha explosiva", "area")
Ranger:add_ability("Volley", "Lluvia de flechas", "area")
Ranger:add_ability("Trap", "Trampa", "special")

function M.init(game) vipzhyla.say("[RANGERS] Habilidades del Ranger cargadas") end
function M.get_class() return Ranger end
function M.get_abilities() return Ranger:get_abilities() end
function M.detect_ability(text)
    local t = text:lower()
    if t:match("flecha") then return { name = "Arrow Shot", type = "physical" }
    elseif t:match("múltiple") then return { name = "Multi Shot", type = "area" }
    elseif t:match("preciso") then return { name = "Aimed Shot", type = "physical" }
    elseif t:match("animal") then return { name = "Animal Companion", type = "summon" }
    elseif t:match("rastreo") then return { name = "Tracking", type = "special" }
    elseif t:match("camuflaje") then return { name = "Camouflage", type = "buff" }
    elseif t:match("explosiva") then return { name = "Explosive Arrow", type = "area" }
    elseif t:match("lluvia") then return { name = "Volley", type = "area" }
    elseif t:match("trampa") then return { name = "Trap", type = "special" }
    end
    return nil
end

return M

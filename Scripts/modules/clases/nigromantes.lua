local ClassBase = require("modules.clases.base")
local M = {}

local Necromancer = ClassBase.new("Nigromante")
Necromancer:add_passive_bonus("intelligence", 2)
Necromancer:add_passive_bonus("wisdom", 1)

Necromancer:add_ability("Curse", "Maldición", "debuff")
Necromancer:add_ability("Death Bolt", "Rayo de muerte", "spell")
Necromancer:add_ability("Drain Life", "Drenaje de vida", "spell")
Necromancer:add_ability("Summon Undead", "Invocar no-muertos", "summon")
Necromancer:add_ability("Bone Prison", "Prisión de huesos", "control")
Necromancer:add_ability("Death Coil", "Espiral de muerte", "spell")
Necromancer:add_ability("Corpse Explosion", "Explosión de cadáver", "area")
Necromancer:add_ability("Life Tap", "Sangría de vida", "spell")
Necromancer:add_ability("Undead Army", "Ejército de no-muertos", "summon")

function M.init(game) vipzhyla.say("[NIGROMANTES] Habilidades del Nigromante cargadas") end
function M.get_class() return Necromancer end
function M.get_abilities() return Necromancer:get_abilities() end
function M.detect_ability(text)
    local t = text:lower()
    if t:match("maldición") then return { name = "Curse", type = "debuff" }
    elseif t:match("muerte") then return { name = "Death Bolt", type = "spell" }
    elseif t:match("drenaje") then return { name = "Drain Life", type = "spell" }
    elseif t:match("no.muerto") then return { name = "Summon Undead", type = "summon" }
    elseif t:match("hueso") then return { name = "Bone Prison", type = "control" }
    elseif t:match("espiral") then return { name = "Death Coil", type = "spell" }
    elseif t:match("explosión") then return { name = "Corpse Explosion", type = "area" }
    end
    return nil
end

return M

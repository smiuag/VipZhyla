--[[
Magos (Wizard) Class Module

Wizards are masters of the arcane arts.
They specialize in:
- Offensive magic (elemental, force)
- Area damage spells
- Mana efficiency
- Spell damage boost

Abilities based on: VipMud Magos.set
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Wizard = ClassBase.new("Mago")

-- Wizard: pure intelligence
Wizard:add_passive_bonus("intelligence", 3)
Wizard:add_passive_bonus("wisdom", 1)

-- Abilities
Wizard:add_ability("Fireball", "Bola de fuego", "spell")
Wizard:add_ability("Lightning Bolt", "Rayo", "spell")
Wizard:add_ability("Ice Storm", "Tormenta de hielo", "area")
Wizard:add_ability("Magic Missile", "Misil mágico", "spell")
Wizard:add_ability("Teleport", "Teleportación", "special")
Wizard:add_ability("Mana Shield", "Escudo de maná", "buff")
Wizard:add_ability("Fireball Barrage", "Lluvia de fuego", "area")
Wizard:add_ability("Disintegrate", "Desintegración", "spell")
Wizard:add_ability("Time Warp", "Distorsión temporal", "special")
Wizard:add_ability("Spell Amplify", "Amplificación de hechizo", "buff")

function M.init(game)
    vipzhyla.say("[MAGOS] Habilidades del Mago cargadas")
end

function M.get_class()
    return Wizard
end

function M.get_abilities()
    return Wizard:get_abilities()
end

function M.detect_ability(text)
    local text_lower = text:lower()

    if text_lower:match("bola de fuego") or text_lower:match("fireball") then
        return { name = "Fireball", type = "spell" }
    elseif text_lower:match("rayo") or text_lower:match("lightning") then
        return { name = "Lightning Bolt", type = "spell" }
    elseif text_lower:match("tormenta de hielo") or text_lower:match("ice storm") then
        return { name = "Ice Storm", type = "area" }
    elseif text_lower:match("misil mágico") or text_lower:match("magic missile") then
        return { name = "Magic Missile", type = "spell" }
    elseif text_lower:match("teleport") or text_lower:match("teleportación") then
        return { name = "Teleport", type = "special" }
    elseif text_lower:match("escudo de maná") then
        return { name = "Mana Shield", type = "buff" }
    elseif text_lower:match("lluvia de fuego") then
        return { name = "Fireball Barrage", type = "area" }
    elseif text_lower:match("desintegración") then
        return { name = "Disintegrate", type = "spell" }
    elseif text_lower:match("temporal") or text_lower:match("time warp") then
        return { name = "Time Warp", type = "special" }
    elseif text_lower:match("amplificación") then
        return { name = "Spell Amplify", type = "buff" }
    end

    return nil
end

return M

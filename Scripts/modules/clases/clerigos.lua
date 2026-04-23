--[[
Clérigos (Cleric) Class Module

Clerics are divine healers and supporters.
They specialize in:
- Healing magic
- Buffs and party support
- Light magic and combat
- Undead turning

Abilities based on: VipMud Clérigos.set
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Cleric = ClassBase.new("Clérigo")

-- Cleric: wisdom and constitution
Cleric:add_passive_bonus("wisdom", 2)
Cleric:add_passive_bonus("constitution", 1)
Cleric:add_passive_bonus("intelligence", 1)

-- Abilities
Cleric:add_ability("Heal", "Curación", "heal")
Cleric:add_ability("Greater Heal", "Curación mayor", "heal")
Cleric:add_ability("Group Heal", "Curación de grupo", "area")
Cleric:add_ability("Holy Light", "Luz sagrada", "spell")
Cleric:add_ability("Blessing", "Bendición", "buff")
Cleric:add_ability("Protection", "Protección divina", "buff")
Cleric:add_ability("Resurrection", "Resurrección", "special")
Cleric:add_ability("Turn Undead", "Repeler no-muertos", "control")
Cleric:add_ability("Sanctuary", "Santuario", "buff")
Cleric:add_ability("Divine Intervention", "Intervención divina", "special")

function M.init(game)
    vipzhyla.say("[CLERIGOS] Habilidades del Clérigo cargadas")
end

function M.get_class()
    return Cleric
end

function M.get_abilities()
    return Cleric:get_abilities()
end

function M.detect_ability(text)
    local text_lower = text:lower()

    if text_lower:match("curación mayor") then
        return { name = "Greater Heal", type = "heal" }
    elseif text_lower:match("curación de grupo") then
        return { name = "Group Heal", type = "area" }
    elseif text_lower:match("curación") or text_lower:match("heal") then
        return { name = "Heal", type = "heal" }
    elseif text_lower:match("luz sagrada") then
        return { name = "Holy Light", type = "spell" }
    elseif text_lower:match("bendición") then
        return { name = "Blessing", type = "buff" }
    elseif text_lower:match("protección") then
        return { name = "Protection", type = "buff" }
    elseif text_lower:match("resurrección") then
        return { name = "Resurrection", type = "special" }
    elseif text_lower:match("no.muerto") then
        return { name = "Turn Undead", type = "control" }
    elseif text_lower:match("santuario") then
        return { name = "Sanctuary", type = "buff" }
    elseif text_lower:match("intervención") then
        return { name = "Divine Intervention", type = "special" }
    end

    return nil
end

return M

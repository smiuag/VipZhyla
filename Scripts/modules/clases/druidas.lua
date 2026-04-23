--[[
Druidas (Druid) Class Module

Druids are nature-attuned casters and healers.
They specialize in:
- Nature magic
- Healing and buffs
- Animal companion
- Shape shifting

Abilities based on: VipMud Druidas.set
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Druid = ClassBase.new("Druida")

-- Druid: wisdom and intelligence
Druid:add_passive_bonus("wisdom", 2)
Druid:add_passive_bonus("intelligence", 1)

-- Abilities
Druid:add_ability("Entangle", "Enredadera", "control")
Druid:add_ability("Nature's Blessing", "Bendición de la naturaleza", "buff")
Druid:add_ability("Regeneration", "Regeneración", "buff")
Druid:add_ability("Summon Animal", "Invocar animal", "summon")
Druid:add_ability("Shapeshift", "Transformarse", "special")
Druid:add_ability("Swarm", "Enjambre", "area")
Druid:add_ability("Earthquake", "Terremoto", "area")
Druid:add_ability("Thorns", "Espinas", "area")
Druid:add_ability("Heal", "Curación", "heal")
Druid:add_ability("Roots", "Raíces", "control")

function M.init(game)
    vipzhyla.say("[DRUIDAS] Habilidades del Druida cargadas")
end

function M.get_class()
    return Druid
end

function M.get_abilities()
    return Druid:get_abilities()
end

function M.detect_ability(text)
    local text_lower = text:lower()

    if text_lower:match("enredadera") then
        return { name = "Entangle", type = "control" }
    elseif text_lower:match("bendición de la naturaleza") then
        return { name = "Nature's Blessing", type = "buff" }
    elseif text_lower:match("regeneración") then
        return { name = "Regeneration", type = "buff" }
    elseif text_lower:match("invocar animal") then
        return { name = "Summon Animal", type = "summon" }
    elseif text_lower:match("transformación") or text_lower:match("transformarse") then
        return { name = "Shapeshift", type = "special" }
    elseif text_lower:match("enjambre") then
        return { name = "Swarm", type = "area" }
    elseif text_lower:match("terremoto") then
        return { name = "Earthquake", type = "area" }
    elseif text_lower:match("espinas") then
        return { name = "Thorns", type = "area" }
    elseif text_lower:match("curación") then
        return { name = "Heal", type = "heal" }
    elseif text_lower:match("raíces") then
        return { name = "Roots", type = "control" }
    end

    return nil
end

return M

--[[
Bardos (Bard) Class Module

Bards are versatile performers and supporters.
They specialize in:
- Songs and auras
- Party buffs and support
- Light melee combat
- Crowd control

Abilities based on: VipMud Bardos.set
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Bard = ClassBase.new("Bardo")

-- Bard: dexterity and charisma
Bard:add_passive_bonus("dexterity", 2)
Bard:add_passive_bonus("charisma", 2)

-- Abilities
Bard:add_ability("Song of Courage", "Canción de coraje", "buff")
Bard:add_ability("Song of Healing", "Canción de curación", "heal")
Bard:add_ability("Song of Slowing", "Canción de ralentización", "control")
Bard:add_ability("Song of Protection", "Canción de protección", "buff")
Bard:add_ability("Inspire", "Inspiración", "buff")
Bard:add_ability("Charm", "Encanto", "control")
Bard:add_ability("Performance", "Actuación", "buff")
Bard:add_ability("Song of Silence", "Canción de silencio", "control")
Bard:add_ability("Misdirection", "Engaño", "special")
Bard:add_ability("Escape", "Escape", "special")

function M.init(game)
    vipzhyla.say("[BARDOS] Habilidades del Bardo cargadas")
end

function M.get_class()
    return Bard
end

function M.get_abilities()
    return Bard:get_abilities()
end

function M.detect_ability(text)
    local text_lower = text:lower()

    if text_lower:match("canción de coraje") then
        return { name = "Song of Courage", type = "buff" }
    elseif text_lower:match("canción de curación") then
        return { name = "Song of Healing", type = "heal" }
    elseif text_lower:match("canción de ralentización") then
        return { name = "Song of Slowing", type = "control" }
    elseif text_lower:match("canción de protección") then
        return { name = "Song of Protection", type = "buff" }
    elseif text_lower:match("inspiración") then
        return { name = "Inspire", type = "buff" }
    elseif text_lower:match("encanto") then
        return { name = "Charm", type = "control" }
    elseif text_lower:match("actuación") then
        return { name = "Performance", type = "buff" }
    elseif text_lower:match("canción de silencio") then
        return { name = "Song of Silence", type = "control" }
    elseif text_lower:match("engaño") then
        return { name = "Misdirection", type = "special" }
    elseif text_lower:match("escape") then
        return { name = "Escape", type = "special" }
    end

    return nil
end

return M

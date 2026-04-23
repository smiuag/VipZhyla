--[[
Soldados (Warrior) Class Module

Warriors are master melee combatants.
They specialize in:
- Weapon mastery (swords, axes, maces)
- Heavy armor and tanking
- Combat techniques
- Physical strength

Abilities based on: VipMud Soldados.set
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Warrior = ClassBase.new("Soldado")

-- Warrior: pure strength
Warrior:add_passive_bonus("strength", 3)
Warrior:add_passive_bonus("constitution", 1)

-- Abilities
Warrior:add_ability("Slash", "Tajo", "physical")
Warrior:add_ability("Power Attack", "Ataque poderoso", "physical")
Warrior:add_ability("Shield Wall", "Muro de escudos", "buff")
Warrior:add_ability("Whirlwind Attack", "Ataque giratorio", "area")
Warrior:add_ability("Riposte", "Contragolpe", "physical")
Warrior:add_ability("Battle Cry", "Grito de batalla", "buff")
Warrior:add_ability("Parry", "Parada", "buff")
Warrior:add_ability("Cleave", "Hendidura", "physical")
Warrior:add_ability("Disarm", "Desarme", "control")
Warrior:add_ability("Last Stand", "Última defensa", "buff")

function M.init(game)
    vipzhyla.say("[SOLDADOS] Habilidades del Soldado cargadas")
end

function M.get_class()
    return Warrior
end

function M.get_abilities()
    return Warrior:get_abilities()
end

function M.detect_ability(text)
    local text_lower = text:lower()

    if text_lower:match("tajo") then
        return { name = "Slash", type = "physical" }
    elseif text_lower:match("ataque poderoso") or text_lower:match("poderoso") then
        return { name = "Power Attack", type = "physical" }
    elseif text_lower:match("escudo") then
        return { name = "Shield Wall", type = "buff" }
    elseif text_lower:match("giratorio") then
        return { name = "Whirlwind Attack", type = "area" }
    elseif text_lower:match("contragolpe") then
        return { name = "Riposte", type = "physical" }
    elseif text_lower:match("grito") then
        return { name = "Battle Cry", type = "buff" }
    elseif text_lower:match("parada") then
        return { name = "Parry", type = "buff" }
    elseif text_lower:match("hendidura") then
        return { name = "Cleave", type = "physical" }
    elseif text_lower:match("desarme") then
        return { name = "Disarm", type = "control" }
    elseif text_lower:match("defensa") then
        return { name = "Last Stand", type = "buff" }
    end

    return nil
end

return M

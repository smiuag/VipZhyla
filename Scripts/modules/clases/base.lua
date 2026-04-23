--[[
Base Class Module - Common functionality for all character classes

Provides:
- Class framework and inheritance
- Common abilities (all classes share some abilities)
- Stat tracking
- Level-up handling
- Experience tracking

Usage:
    local ClassBase = require("modules.clases.base")
    local Shaman = ClassBase:new("Chamán")
    Shaman:add_ability("Shock", "Hechizo de rayo")
]]

local M = {}

-- Base class prototype
local ClassPrototype = {}
ClassPrototype.__index = ClassPrototype

-- Create new class
function M.new(class_name)
    local class = {
        name = class_name,
        abilities = {},
        passive_bonuses = {},
        stats = {
            strength = 10,
            dexterity = 10,
            constitution = 10,
            intelligence = 10,
            wisdom = 10,
            charisma = 10,
        },
    }

    setmetatable(class, ClassPrototype)
    return class
end

-- Add ability to class
function ClassPrototype:add_ability(ability_name, description, ability_type)
    table.insert(self.abilities, {
        name = ability_name,
        description = description,
        type = ability_type or "ability",
        level_required = 1,
    })
end

-- Add passive bonus
function ClassPrototype:add_passive_bonus(stat, bonus)
    self.passive_bonuses[stat] = (self.passive_bonuses[stat] or 0) + bonus
end

-- Get ability
function ClassPrototype:get_ability(ability_name)
    for _, ability in ipairs(self.abilities) do
        if ability.name == ability_name then
            return ability
        end
    end
    return nil
end

-- List all abilities
function ClassPrototype:get_abilities()
    return self.abilities
end

-- Get stat with bonuses
function ClassPrototype:get_stat(stat_name)
    return (self.stats[stat_name] or 0) + (self.passive_bonuses[stat_name] or 0)
end

-- Log class info
function ClassPrototype:log_info()
    vipzhyla.say("[CLASE] " .. self.name)
    vipzhyla.say("  Habilidades: " .. #self.abilities)
    for i, ability in ipairs(self.abilities) do
        vipzhyla.say("    " .. i .. ". " .. ability.name .. " - " .. ability.description)
    end
end

return M

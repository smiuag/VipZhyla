--[[
Brujos (Warlock) Class Module
Practitioners of hexes and ritual magic. Mix of debuff curses and
defensive enchantments.
]]

local ClassBase = require("modules.clases.base")
local M = {}

local Warlock = ClassBase.new("Brujo")
Warlock:add_passive_bonus("intelligence", 2)
Warlock:add_passive_bonus("wisdom", 2)

for _, a in ipairs({"Hex", "Potion", "Spell Steal", "Blight", "Ward", "Enchant"}) do
    Warlock:add_ability(a, a, "spell")
end

function M.init(game) vipzhyla.say("[BRUJOS] Brujo cargado") end
function M.get_class() return Warlock end
function M.get_abilities() return Warlock:get_abilities() end

function M.detect_ability(text)
    if not text then return nil end
    local t = text:lower()
    if t:match("hechizo robado") or t:match("spell steal") then
        return { name = "Spell Steal", type = "spell" }
    elseif t:match("hex") or t:match("conjuro") then
        return { name = "Hex", type = "debuff" }
    elseif t:match("poción") or t:match("potion") then
        return { name = "Potion", type = "spell" }
    elseif t:match("plaga") or t:match("blight") then
        return { name = "Blight", type = "debuff" }
    elseif t:match("guarda") or t:match("ward") then
        return { name = "Ward", type = "buff" }
    elseif t:match("encantamiento") or t:match("enchant") then
        return { name = "Enchant", type = "buff" }
    end
    return nil
end

return M

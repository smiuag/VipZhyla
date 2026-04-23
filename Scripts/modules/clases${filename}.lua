local ClassBase = require("modules.clases.base")
local M = {}

local CaballeroOscuro = ClassBase.new("Caballero_Oscuro")
CaballeroOscuro:add_passive_bonus("strength", 1)
CaballeroOscuro:add_passive_bonus("intelligence", 1)

CaballeroOscuro:add_ability("Ability1", "Habilidad 1", "physical")
CaballeroOscuro:add_ability("Ability2", "Habilidad 2", "spell")

function M.init(game) end
function M.get_class() return CaballeroOscuro end
function M.get_abilities() return CaballeroOscuro:get_abilities() end
function M.detect_ability(text) return nil end

return M

--[[
Movimiento Module - Movement and navigation

Manages:
- Direction detection and validation
- Room changes and navigation
- Movement triggers and state
- Navigation audio feedback
- Travel mode detection

Directions (Spanish):
- Cardinal: norte, sur, este, oeste
- Diagonal: noreste, noroeste, sudeste, sudoeste
- Vertical: arriba, abajo
- Special: dentro, fuera, entrada, salida, etc.

Ported from: Movimiento_*.set (276 lines)
--]]

local M = {}
local helpers = require("lib.helpers")

-- Valid directions in Spanish
local DIRECTIONS = {
    -- Cardinal
    norte = { name = "norte", short = "n", emoji = "↑" },
    sur = { name = "sur", short = "s", emoji = "↓" },
    este = { name = "este", short = "e", emoji = "→" },
    oeste = { name = "oeste", short = "o", emoji = "←" },

    -- Diagonal
    noreste = { name = "noreste", short = "ne", emoji = "↗" },
    noroeste = { name = "noroeste", short = "no", emoji = "↖" },
    sudeste = { name = "sudeste", short = "se", emoji = "↘" },
    sudoeste = { name = "sudoeste", short = "so", emoji = "↙" },

    -- Vertical
    arriba = { name = "arriba", short = "a", emoji = "⬆" },
    abajo = { name = "abajo", short = "ab", emoji = "⬇" },

    -- Special
    dentro = { name = "dentro", short = "d", emoji = "→" },
    fuera = { name = "fuera", short = "f", emoji = "←" },
    entrada = { name = "entrada", short = "ent", emoji = "📍" },
    salida = { name = "salida", short = "sal", emoji = "🚪" },
}

-- Movement state
local STATE = {
    last_direction = "",
    last_room = "",
    is_moving = false,
    last_move_time = 0,
    movement_speed = 0,  -- 0=normal, 1=turbo, 2=ultra (from ModoPath)
}

-- Initialize module
function M.init(game)
    vipzhyla.say("[MOVIMIENTO] Sistema de navegación inicializado")
    vipzhyla.say("[MOVIMIENTO] Direcciones disponibles: " .. M.get_directions_string())
end

-- Handle MUD text for movement-related patterns
function M.on_message(channel, text)
    -- Detect movement messages and reactions
    -- Example: "Entras en..." = direction inside
    -- Example: "Sales de..." = direction outside
    -- Example: "X ha entrado" = someone entered
    -- Example: "X se ha ido hacia el..." = someone left

    -- For now, basic detection
    if text:match("entras en") or text:match("entras por") then
        M.on_movement_detected("dentro")
    elseif text:match("sales de") or text:match("sales por") then
        M.on_movement_detected("fuera")
    end
end

-- Handle GMCP room data (authoritative source for room changes)
function M.on_gmcp(module_name, data)
    if module_name == "Room.Info" then
        M.on_room_changed(data)
    elseif module_name == "Room.Actual" then
        M.on_room_actual(data)
    elseif module_name == "Room.Movimiento" then
        M.on_room_movimiento(data)
    end
end

-- Called when room changes (from GMCP Room.Info)
function M.on_room_changed(room_data)
    local new_room = room_data.name or "Unknown"

    -- If room changed, announce movement
    if STATE.last_room ~= "" and STATE.last_room ~= new_room then
        vipzhyla.say("[MOVIMIENTO] Entrado a: " .. new_room)
    end

    STATE.last_room = new_room
    STATE.is_moving = false
end

-- Called on room actual data
function M.on_room_actual(room_name)
    STATE.last_room = room_name
end

-- Called on movement direction (GMCP Room.Movimiento)
function M.on_room_movimiento(direction)
    M.on_movement_detected(direction)
end

-- Internal: Handle movement detection
function M.on_movement_detected(direction)
    STATE.last_direction = direction
    STATE.last_move_time = os.time()
    STATE.is_moving = true

    -- Play movement audio (optional)
    -- vipzhyla.play_sound("RL/Movimiento/pasos.wav")
end

-- Execute movement command
function M.move(direction)
    if not M.is_valid_direction(direction) then
        vipzhyla.say("[MOVIMIENTO ERROR] Dirección inválida: " .. direction)
        return false
    end

    vipzhyla.send_command(direction)
    STATE.last_direction = direction
    STATE.last_move_time = os.time()

    return true
end

-- Check if direction is valid
function M.is_valid_direction(direction)
    return DIRECTIONS[direction] ~= nil
end

-- Get direction info
function M.get_direction(direction)
    return DIRECTIONS[direction]
end

-- Get all directions
function M.get_all_directions()
    local dirs = {}
    for key, data in pairs(DIRECTIONS) do
        table.insert(dirs, key)
    end
    return dirs
end

-- Get directions as formatted string
function M.get_directions_string()
    local dirs = {}
    for key, data in pairs(DIRECTIONS) do
        table.insert(dirs, key)
    end
    table.sort(dirs)
    return table.concat(dirs, ", ")
end

-- Get last movement
function M.get_last_direction()
    return STATE.last_direction
end

-- Get current room
function M.get_current_room()
    return STATE.last_room
end

-- Check if currently moving
function M.is_moving()
    return STATE.is_moving
end

-- Set movement speed mode (from configuracion.modo_path)
function M.set_movement_speed(speed)
    -- speed: 0=normal, 1=turbo, 2=ultra
    STATE.movement_speed = speed
end

-- Get movement speed
function M.get_movement_speed()
    return STATE.movement_speed
end

-- Movement speed affects description filtering
function M.should_filter_descriptions()
    return STATE.movement_speed > 0
end

function M.should_filter_aggressive()
    return STATE.movement_speed == 2  -- Ultra mode = max filtering
end

-- Quick movement aliases
function M.n() return M.move("norte") end
function M.s() return M.move("sur") end
function M.e() return M.move("este") end
function M.o() return M.move("oeste") end
function M.ne() return M.move("noreste") end
function M.no() return M.move("noroeste") end
function M.se() return M.move("sudeste") end
function M.so() return M.move("sudoeste") end
function M.a() return M.move("arriba") end
function M.ab() return M.move("abajo") end
function M.d() return M.move("dentro") end
function M.f() return M.move("fuera") end

-- Debug/info
function M.log_status()
    vipzhyla.say("[MOVIMIENTO STATUS]")
    vipzhyla.say("  Sala actual: " .. STATE.last_room)
    vipzhyla.say("  Última dirección: " .. STATE.last_direction)
    vipzhyla.say("  En movimiento: " .. (STATE.is_moving and "sí" or "no"))
    vipzhyla.say("  Velocidad: " .. ({"normal", "turbo", "ultra"}[STATE.movement_speed + 1]))
end

return M

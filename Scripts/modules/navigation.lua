--[[
Navigation Module - Path finding and route management

Manages:
- Room database from Paths/*.set scripts
- Simple path following (without recording)
- Route validation and execution
- Navigation helper functions

Note: Path recording/playback deferred to Phase 6E
This module provides foundation for routes.

Ported from: Paths/*.set (700 lines, 15 files)
--]]

local M = {}

-- Room database (will be populated from Paths scripts in Phase 6E)
local ROOMS = {}

-- Known routes (simple hardcoded for MVP, will expand)
local ROUTES = {
    -- Format: route_name = { room_sequence }
    -- Example: eldor = { "plaza", "tienda", "posada", "eldor_center" }
}

-- Navigation state
local NAV_STATE = {
    current_route = nil,
    route_position = 0,
    is_following_route = false,
}

-- Initialize module
function M.init(game)
    vipzhyla.say("[NAVIGATION] Sistema de rutas inicializado (MVP mode)")
    -- In Phase 6E, load full room database and routes
end

-- Register a room (called from path scripts)
function M.register_room(room_name, exits, description)
    ROOMS[room_name] = {
        name = room_name,
        exits = exits or {},
        description = description or "",
    }
end

-- Register a route
function M.register_route(route_name, room_sequence)
    if type(room_sequence) == "string" then
        -- Split by pipes if provided as string
        room_sequence = {}
        for room in room_sequence:gmatch("[^|]+") do
            table.insert(room_sequence, room)
        end
    end

    ROUTES[route_name] = room_sequence
    vipzhyla.say("[NAVIGATION] Ruta registrada: " .. route_name)
end

-- Get all available routes
function M.get_routes()
    local route_list = {}
    for route_name, _ in pairs(ROUTES) do
        table.insert(route_list, route_name)
    end
    return route_list
end

-- Get route details
function M.get_route(route_name)
    return ROUTES[route_name]
end

-- Start following a route
function M.follow_route(route_name)
    local route = ROUTES[route_name]
    if not route then
        vipzhyla.say("[NAVIGATION ERROR] Ruta no encontrada: " .. route_name)
        return false
    end

    NAV_STATE.current_route = route_name
    NAV_STATE.route_position = 1
    NAV_STATE.is_following_route = true

    vipzhyla.announce("Siguiendo ruta: " .. route_name)
    return true
end

-- Continue following current route
function M.continue_route()
    if not NAV_STATE.is_following_route or not NAV_STATE.current_route then
        return false
    end

    local route = ROUTES[NAV_STATE.current_route]
    if not route then
        M.stop_route()
        return false
    end

    -- Check if route complete
    if NAV_STATE.route_position > #route then
        vipzhyla.announce("Ruta completada: " .. NAV_STATE.current_route)
        M.stop_route()
        return false
    end

    -- Get next step
    local next_room = route[NAV_STATE.route_position]
    NAV_STATE.route_position = NAV_STATE.route_position + 1

    vipzhyla.send_command(next_room)
    return true
end

-- Stop following route
function M.stop_route()
    NAV_STATE.is_following_route = false
    NAV_STATE.current_route = nil
    NAV_STATE.route_position = 0
    vipzhyla.say("[NAVIGATION] Ruta detenida")
end

-- Get current route status
function M.get_route_status()
    if not NAV_STATE.is_following_route then
        return {
            active = false,
            current_route = nil,
            position = 0,
        }
    end

    return {
        active = true,
        current_route = NAV_STATE.current_route,
        position = NAV_STATE.route_position,
        total_steps = #ROUTES[NAV_STATE.current_route],
        percent_complete = (NAV_STATE.route_position / #ROUTES[NAV_STATE.current_route]) * 100,
    }
end

-- Find shortest route between two rooms (simple BFS)
-- Note: Full implementation in Phase 6E
function M.find_route(start_room, end_room)
    -- For MVP, just return hardcoded routes
    -- Full pathfinding in Phase 6E

    vipzhyla.say("[NAVIGATION] Búsqueda de rutas no disponible en MVP")
    return nil
end

-- Validate route (check all rooms exist)
function M.validate_route(route_name)
    local route = ROUTES[route_name]
    if not route then
        return false, "Ruta no encontrada"
    end

    for _, room in ipairs(route) do
        if not ROOMS[room] then
            return false, "Sala desconocida en ruta: " .. room
        end
    end

    return true, "OK"
end

-- Log routes info
function M.log_routes()
    vipzhyla.say("[RUTAS]")
    local route_count = 0
    for route_name, route in pairs(ROUTES) do
        vipzhyla.say("  " .. route_name .. " (" .. #route .. " pasos)")
        route_count = route_count + 1
    end
    vipzhyla.say("Total: " .. route_count .. " rutas")
end

-- Log rooms info
function M.log_rooms()
    vipzhyla.say("[SALAS]")
    local room_count = 0
    for room_name, _ in pairs(ROOMS) do
        vipzhyla.say("  " .. room_name)
        room_count = room_count + 1
    end
    vipzhyla.say("Total: " .. room_count .. " salas")
end

return M

--[[
Oficios (Professions) Module - Profession framework + submodule integration

Manages all 5 player professions:
  - minero  (Miner)    -> modules/oficios/minero.lua
  - herrero (Smith)    -> modules/oficios/herrero.lua
  - marinero (Sailor)  -> modules/oficios/marinero.lua
  - jornalero (Day-Laborer) -> modules/oficios/jornalero.lua
  - crear   (Crafter)  -> modules/oficios/crear.lua

Each submodule provides text-pattern detection (start, turn, success,
failure, stop, event) for its profession's MUD output. This top-level
module:
  1. Loads each submodule via pcall (resilient if a file is missing).
  2. Tracks per-profession session state (turn/success/failure counters).
  3. Routes incoming MUD text to the active profession's detectors and
     auto-updates counters.
  4. Integrates with `game.estadisticas` (Phase 7A) so successes/failures
     count toward gameplay stats.

Phase 7C audit: previously this file only kept counters and never loaded
the submodules — meaning none of their patterns were ever consulted.
]]

local M = {}

-- ===== Profession Session State =====

local function new_profession(name)
    return {
        name = name,
        active = false,
        turn_count = 0,
        success_count = 0,
        failure_count = 0,
        event_count = 0,
        last_action = nil,
        last_result = nil,
        last_event = nil,
        started_at = 0,
    }
end

local professions = {
    minero    = new_profession("Minero"),
    herrero   = new_profession("Herrero"),
    marinero  = new_profession("Marinero"),
    jornalero = new_profession("Jornalero"),
    crear     = new_profession("Crear"),
}

-- Loaded submodules, keyed by profession name.
local submodules = {}

-- Reference to the global `game` table (set in init).
local game_ref = nil

-- ===== Submodule Loading =====

local function load_submodule(prof_name)
    local ok, mod = pcall(require, "modules.oficios." .. prof_name)
    if ok and type(mod) == "table" then
        submodules[prof_name] = mod
        if type(mod.init) == "function" and game_ref then
            pcall(mod.init, game_ref)
        end
        return true
    end
    if vipzhyla and vipzhyla.say then
        vipzhyla.say("[OFICIOS] WARN: failed to load submodule '" .. prof_name .. "'")
    end
    return false
end

function M.init(game)
    game_ref = game
    game.professions = professions
    game.oficios = game.oficios or {}
    game.oficios.submodules = submodules

    -- Load every known profession submodule.
    local loaded = 0
    for prof_name, _ in pairs(professions) do
        if load_submodule(prof_name) then
            loaded = loaded + 1
        end
    end

    if vipzhyla and vipzhyla.say then
        vipzhyla.say("[OFICIOS] Sistema de oficios listo (" .. loaded .. "/5 submódulos)")
    end
end

-- ===== Active Profession Management =====

function M.get_active_profession()
    for name, prof in pairs(professions) do
        if prof.active then
            return name, prof
        end
    end
    return nil, nil
end

function M.start_profession(name)
    if not professions[name] then
        return false
    end
    -- Stop whatever is currently active first.
    M.stop_profession()

    local prof = professions[name]
    prof.active = true
    prof.turn_count = 0
    prof.success_count = 0
    prof.failure_count = 0
    prof.event_count = 0
    prof.last_action = nil
    prof.last_result = nil
    prof.last_event = nil
    prof.started_at = os.time()

    if vipzhyla and vipzhyla.announce then
        vipzhyla.announce("Oficio iniciado: " .. prof.name)
    end
    return true
end

function M.stop_profession()
    local stopped = nil
    for name, prof in pairs(professions) do
        if prof.active then
            stopped = name
        end
        prof.active = false
    end
    if stopped and vipzhyla and vipzhyla.announce then
        vipzhyla.announce("Oficio detenido: " .. professions[stopped].name)
    end
end

function M.is_active(name)
    return professions[name] and professions[name].active or false
end

-- ===== Counter Updates =====

function M.increment_turn(name)
    if professions[name] then
        professions[name].turn_count = professions[name].turn_count + 1
        return professions[name].turn_count
    end
    return nil
end

function M.register_success(name, action)
    if professions[name] then
        professions[name].success_count = professions[name].success_count + 1
        professions[name].last_action = action
        professions[name].last_result = "success"

        -- Phase 7A integration: feed item-found stat for crafting/gathering.
        if game_ref and game_ref.modules and game_ref.modules.estadisticas then
            pcall(game_ref.modules.estadisticas.record_item_found, name)
        end
    end
end

function M.register_failure(name, action, reason)
    if professions[name] then
        professions[name].failure_count = professions[name].failure_count + 1
        professions[name].last_action = action
        professions[name].last_result = reason or "failure"
    end
end

function M.register_event(name, event_kind)
    if professions[name] then
        professions[name].event_count = professions[name].event_count + 1
        professions[name].last_event = event_kind

        -- Phase 7A integration: log event for the events log.
        if game_ref and game_ref.modules and game_ref.modules.eventos then
            pcall(
                game_ref.modules.eventos.log_event,
                "special",
                "Oficio " .. name .. ": " .. tostring(event_kind),
                { profession = name, event = event_kind }
            )
        end
    end
end

-- ===== Pattern Detection (text dispatch) =====

local function call(submod, fn_name, text)
    if not submod or not submod[fn_name] then
        return nil
    end
    local ok, result = pcall(submod[fn_name], text)
    if ok then return result end
    return nil
end

function M.process_message(text)
    --[[
    Route a MUD message to the active profession's detectors.
    Auto-updates counters for any detected event. Safe to call from
    `game.on_mud_message`.

    Returns the kind of detection ("start"|"turn"|"success"|"failure"
    |"stop"|"event") or nil if nothing matched.
    ]]
    if not text or text == "" then return nil end

    local active_name = nil
    for name, prof in pairs(professions) do
        if prof.active then active_name = name; break end
    end
    if not active_name then return nil end

    local sub = submodules[active_name]
    if not sub then return nil end

    -- Order matters: start/stop are unambiguous, then result, then turn.
    if call(sub, "detect_start", text) then return "start" end

    local stop_hit = call(sub, "detect_stop", text)
    if stop_hit then
        M.stop_profession()
        return "stop"
    end

    local fail = call(sub, "detect_failure", text)
    if fail then
        M.register_failure(active_name, fail, fail)
        return "failure"
    end

    if call(sub, "detect_success", text) then
        M.register_success(active_name, "success")
        return "success"
    end

    -- Marinero exposes detect_cast/detect_bite instead of detect_turn.
    if call(sub, "detect_turn", text) or call(sub, "detect_cast", text) then
        M.increment_turn(active_name)
        return "turn"
    end

    if call(sub, "detect_bite", text) then
        -- Bite is a "near-success" cue for marinero — count as a turn.
        M.increment_turn(active_name)
        return "turn"
    end

    -- crear has detect_component (a partial-progress signal).
    if call(sub, "detect_component", text) then
        M.increment_turn(active_name)
        return "turn"
    end

    local event_kind = call(sub, "detect_event", text)
    if event_kind then
        M.register_event(active_name, event_kind)
        return "event"
    end

    return nil
end

-- Hook so `game.on_mud_message` dispatch picks us up automatically.
function M.on_message(_channel, text)
    M.process_message(text)
end

-- ===== Queries =====

function M.get_profession(name)
    return professions[name]
end

function M.get_all_professions()
    return professions
end

function M.get_submodule(name)
    return submodules[name]
end

function M.get_stats(name)
    local prof = professions[name]
    if not prof then return nil end
    return {
        turns       = prof.turn_count,
        successes   = prof.success_count,
        failures    = prof.failure_count,
        events      = prof.event_count,
        last_action = prof.last_action,
        last_result = prof.last_result,
        last_event  = prof.last_event,
        active      = prof.active,
        elapsed     = prof.started_at > 0 and (os.time() - prof.started_at) or 0,
    }
end

function M.format_stats(name)
    local s = M.get_stats(name)
    if not s then return "Oficio desconocido: " .. tostring(name) end
    return string.format(
        "%s — turnos: %d, éxitos: %d, fallos: %d, eventos: %d (activo: %s)",
        professions[name].name,
        s.turns, s.successes, s.failures, s.events,
        s.active and "sí" or "no"
    )
end

return M

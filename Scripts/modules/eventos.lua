--[[
Eventos/Server Events System - Event logging and handling

Tracks server events, quests, achievements, and special game events.
Provides event logging, pattern detection, and event callbacks.

Phase 7A: Complete game state management
]]

local M = {}

-- Event types
local EVENT_TYPES = {
    quest = "Quest",
    achievement = "Achievement",
    combat = "Combat",
    social = "Social",
    economic = "Economic",
    system = "System",
    special = "Special",
}

-- Event detection patterns
local EVENT_PATTERNS = {
    -- Quest events
    quest_accepted = {
        "aceptas la mision",
        "quest accepted",
        "misin aceptada",
    },
    quest_completed = {
        "Completas la mision",
        "quest completed",
        "Misin completada",
    },
    quest_failed = {
        "Fallas en la mision",
        "quest failed",
        "has failed the",
    },

    -- Combat events
    defeated_enemy = {
        "Derrotas a",
        "You defeat",
        "has been defeated",
        "defeated",
    },
    player_defeated = {
        "Ha sido derrotado",
        "You have been defeated",
        "Eres derrotado",
    },
    level_up = {
        "Subes de nivel",
        "You have advanced",
        "level up",
        "You gain a level",
    },

    -- Social events
    player_join = {
        "entra en",
        "has entered",
        "arrives from",
        "Llega desde",
    },
    player_leave = {
        "se marcha hacia",
        "has left for",
        "departs for",
        "Se va hacia",
    },
    player_death = {
        "muere",
        "dies",
        "has been slain",
        "perece",
    },

    -- Economic events
    item_drop = {
        "Obtienes",
        "You receive",
        "obtienen",
    },
    item_loss = {
        "pierdes",
        "loses",
        "drop",
        "You drop",
    },
    gold_gain = {
        "ganas",
        "You gain",
        "recibir oro",
    },

    -- Special events
    server_restart = {
        "servidor se reinicia",
        "server is restarting",
        "Se va a reiniciar",
    },
    maintenance = {
        "mantenimiento",
        "maintenance",
        "under maintenance",
    },
}

-- Active events log
local events_log = {}
local event_id_counter = 0

-- Event callbacks
local event_callbacks = {}

function M.init(game)
    game.eventos = game.eventos or {}
    game.eventos.log = events_log
    game.eventos.types = EVENT_TYPES
end

--[[ ===== Event Logging ===== ]]

function M.log_event(event_type, description, metadata)
    --[[
    Log an event.

    Args:
        event_type: Type of event (quest, achievement, combat, etc.)
        description: Event description
        metadata: Optional table with additional data

    Returns:
        Event ID
    ]]

    event_id_counter = event_id_counter + 1
    local event = {
        id = event_id_counter,
        type = event_type,
        description = description,
        timestamp = os.time(),
        metadata = metadata or {},
    }

    table.insert(events_log, event)

    -- Trigger callbacks
    if event_callbacks[event_type] then
        for _, callback in ipairs(event_callbacks[event_type]) do
            pcall(callback, event)
        end
    end

    vipzhyla.announce("Evento: " .. description)

    return event_id_counter
end

function M.get_event(event_id)
    --[[Get event by ID.]]
    for _, event in ipairs(events_log) do
        if event.id == event_id then
            return event
        end
    end
    return nil
end

function M.get_events_by_type(event_type)
    --[[Get all events of a specific type.]]
    local events = {}
    for _, event in ipairs(events_log) do
        if event.type == event_type then
            table.insert(events, event)
        end
    end
    return events
end

function M.get_events_since(seconds_ago)
    --[[Get events from last N seconds.]]
    local events = {}
    local cutoff = os.time() - seconds_ago

    for _, event in ipairs(events_log) do
        if event.timestamp >= cutoff then
            table.insert(events, event)
        end
    end

    return events
end

function M.get_recent_events(count)
    --[[Get last N events.]]
    local events = {}
    local start = math.max(1, #events_log - count + 1)

    for i = start, #events_log do
        table.insert(events, events_log[i])
    end

    return events
end

function M.count_events()
    --[[Count total logged events.]]
    return #events_log
end

--[[ ===== Pattern Detection ===== ]]

function M.detect_event(text)
    --[[
    Detect event from MUD message.

    Returns:
        Event name if detected, nil otherwise
    ]]

    for event_name, patterns in pairs(EVENT_PATTERNS) do
        for _, pattern in ipairs(patterns) do
            if string.find(text:lower(), pattern:lower(), 1, true) then
                return event_name
            end
        end
    end

    return nil
end

function M.process_message(text)
    --[[
    Auto-detect and log events from MUD message.
    Called from game.on_mud_message().
    ]]

    local event_name = M.detect_event(text)
    if event_name then
        M.log_event("detected", event_name .. ": " .. text, {
            text = text,
            pattern = event_name,
        })
        return event_name
    end

    return nil
end

--[[ ===== Event Callbacks ===== ]]

function M.register_event_callback(event_type, callback)
    --[[
    Register a callback for event type.

    Args:
        event_type: Type to listen for
        callback: Function to call when event fires
    ]]

    if not event_callbacks[event_type] then
        event_callbacks[event_type] = {}
    end

    table.insert(event_callbacks[event_type], callback)
    return #event_callbacks[event_type]
end

function M.unregister_event_callback(event_type, callback_id)
    --[[Remove a callback.]]
    if event_callbacks[event_type] then
        table.remove(event_callbacks[event_type], callback_id)
    end
end

--[[ ===== Quest Events ===== ]]

function M.log_quest_accepted(quest_name)
    --[[Log quest accepted event.]]
    return M.log_event("quest", "Aceptaste: " .. quest_name, {
        subtype = "accepted",
        quest = quest_name,
    })
end

function M.log_quest_completed(quest_name)
    --[[Log quest completed event.]]
    return M.log_event("quest", "Completaste: " .. quest_name, {
        subtype = "completed",
        quest = quest_name,
    })
end

function M.log_quest_failed(quest_name)
    --[[Log quest failed event.]]
    return M.log_event("quest", "Fallaste en: " .. quest_name, {
        subtype = "failed",
        quest = quest_name,
    })
end

--[[ ===== Combat Events ===== ]]

function M.log_combat_victory(enemy_name, experience)
    --[[Log combat victory.]]
    return M.log_event("combat", "Derrotaste a " .. enemy_name, {
        subtype = "victory",
        enemy = enemy_name,
        experience = experience or 0,
    })
end

function M.log_combat_defeat(enemy_name)
    --[[Log combat defeat.]]
    return M.log_event("combat", "Fuiste derrotado por " .. enemy_name, {
        subtype = "defeat",
        enemy = enemy_name,
    })
end

function M.log_level_up(new_level)
    --[[Log level up.]]
    return M.log_event("combat", "Subiste a nivel " .. new_level, {
        subtype = "level_up",
        level = new_level,
    })
end

--[[ ===== Social Events ===== ]]

function M.log_player_joined(player_name)
    --[[Log player joined.]]
    return M.log_event("social", player_name .. " entra en la sala", {
        subtype = "player_joined",
        player = player_name,
    })
end

function M.log_player_left(player_name)
    --[[Log player left.]]
    return M.log_event("social", player_name .. " se marcha", {
        subtype = "player_left",
        player = player_name,
    })
end

function M.log_player_death(player_name)
    --[[Log player death.]]
    return M.log_event("social", player_name .. " ha muerto", {
        subtype = "player_death",
        player = player_name,
    })
end

--[[ ===== Economic Events ===== ]]

function M.log_item_obtained(item_name, quantity)
    --[[Log item obtained.]]
    return M.log_event("economic", "Obtienes " .. (quantity or 1) .. "x " .. item_name, {
        subtype = "item_obtained",
        item = item_name,
        quantity = quantity or 1,
    })
end

function M.log_item_lost(item_name, quantity)
    --[[Log item lost.]]
    return M.log_event("economic", "Pierdes " .. (quantity or 1) .. "x " .. item_name, {
        subtype = "item_lost",
        item = item_name,
        quantity = quantity or 1,
    })
end

function M.log_gold_transaction(amount, type_str)
    --[[Log gold transaction (type: gain/loss).]]
    local desc = type_str == "gain" and ("Ganas " .. amount .. " oro") or ("Pierdes " .. amount .. " oro")
    return M.log_event("economic", desc, {
        subtype = "gold_" .. type_str,
        amount = amount,
    })
end

--[[ ===== System Events ===== ]]

function M.log_system_event(description, subtype)
    --[[Log generic system event.]]
    return M.log_event("system", description, {
        subtype = subtype or "generic",
    })
end

function M.log_server_restart()
    --[[Log server restart event.]]
    return M.log_event("system", "Servidor reiniciandose", {
        subtype = "server_restart",
    })
end

function M.log_maintenance()
    --[[Log server maintenance.]]
    return M.log_event("system", "Servidor en mantenimiento", {
        subtype = "maintenance",
    })
end

--[[ ===== Event Statistics ===== ]]

function M.get_event_stats()
    --[[Get summary statistics of logged events.]]
    local stats = {
        total = #events_log,
        by_type = {},
    }

    for _, event in ipairs(events_log) do
        if not stats.by_type[event.type] then
            stats.by_type[event.type] = 0
        end
        stats.by_type[event.type] = stats.by_type[event.type] + 1
    end

    return stats
end

function M.get_event_summary()
    --[[Get human-readable event summary.]]
    local stats = M.get_event_stats()
    local lines = {}

    table.insert(lines, "=== EVENTOS ===")
    table.insert(lines, "Total registrados: " .. stats.total)
    table.insert(lines, "")
    table.insert(lines, "Por tipo:")

    for event_type, count in pairs(stats.by_type) do
        table.insert(lines, "  " .. event_type .. ": " .. count)
    end

    return table.concat(lines, "\n")
end

--[[ ===== Testing/Reset ===== ]]

function M.clear_events()
    --[[Clear all events (for testing).]]
    events_log = {}
    event_id_counter = 0
    vipzhyla.announce("Eventos borrados")
end

function M.get_all_events()
    --[[Return raw events log.]]
    return events_log
end

return M

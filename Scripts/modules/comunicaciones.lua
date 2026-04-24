--[[
Comunicaciones Module - Channel system and message handling

Manages:
- 11 game channels (Bando, Telepátia, Sala, etc.)
- Message history per channel (max 99 per channel, VipMud standard)
- Channel filtering and muting
- TTS announcements per channel
- Pattern detection for GMCP fallback

Ported from: Comunicaciones.set (245 lines, 75 commands)
--]]

local M = {}
local helpers = require("lib.helpers")

-- Channel configuration
local CHANNELS = {
    bando = { name = "Bando", pattern = "%[bando%]", muted = false, history = {} },
    telepathy = { name = "Telepátia", pattern = "%[telepát", muted = false, history = {} },
    sala = { name = "Sala", pattern = "^[^%[]", muted = false, history = {} },  -- Default/general
    gremio = { name = "Gremio", pattern = "%[gremio%]", muted = false, history = {} },
    familia = { name = "Familia", pattern = "%[familia%]", muted = false, history = {} },
    rol = { name = "Rol", pattern = "%[rol%]", muted = false, history = {} },
    ciudadania = { name = "Ciudadanía", pattern = "%[ciudad", muted = false, history = {} },
    chat = { name = "Chat", pattern = "%[chat%]", muted = false, history = {} },
    eventos = { name = "Eventos", pattern = "%[evento", muted = false, history = {} },
    sistema = { name = "Sistema", pattern = "^%-%-", muted = false, history = {} },
    especial = { name = "Especial", pattern = "%[especial%]", muted = false, history = {} },
}

local MAX_HISTORY_PER_CHANNEL = 99

-- Initialize module
function M.init(game)
    vipzhyla.say("[COMUNICACIONES] Initializing channel system with 11 channels")

    -- Register pattern-based triggers for each channel (fallback when GMCP not available)
    for channel_key, channel_data in pairs(CHANNELS) do
        -- Pattern is used for text-based detection
        -- Will be registered as triggers by Python when GMCP available
    end

    vipzhyla.announce("Sistema de canales iniciado")
end

-- Detect channel from text (fallback pattern matching)
function M.detect_channel(text)
    -- GMCP is primary - if module is Comm.Channel, that's authoritative
    -- This is fallback for non-GMCP servers

    -- Check each channel pattern
    if text:match("%[bando%]") or text:match("%(bando%)") then
        return "bando"
    elseif text:match("%[telepát") then
        return "telepathy"
    elseif text:match("%[gremio%]") or text:match("%(gremio%)") then
        return "gremio"
    elseif text:match("%[familia%]") then
        return "familia"
    elseif text:match("%[rol%]") then
        return "rol"
    elseif text:match("%[ciudad") then
        return "ciudadania"
    elseif text:match("%[chat%]") or text:match("%(chat%)") then
        return "chat"
    elseif text:match("%[evento") then
        return "eventos"
    elseif text:match("%[especial%]") then
        return "especial"
    elseif text:match("^%-%-") then
        return "sistema"
    else
        return "sala"  -- Default to room/general
    end
end

-- Handle incoming MUD message
function M.on_message(channel_key, text)
    if not channel_key or channel_key == "" then
        channel_key = M.detect_channel(text)
    end

    local channel = CHANNELS[channel_key]
    if not channel then
        channel = CHANNELS["sala"]
    end

    -- Check if channel is muted
    if channel.muted then
        return
    end

    -- Add to history
    M.add_to_history(channel_key, text)

    -- TTS announcement (verbosity depends on config)
    -- vipzhyla.announce(text) would be called here with proper verbosity checking
end

-- Handle GMCP Comm.Channel (GMCP is authoritative)
function M.on_gmcp(module_name, data)
    if module_name ~= "Comm.Channel" then
        return
    end

    -- GMCP format: { channel = "bando", talker = "Name", text = "message" }
    local channel_name = (data.channel or "general"):lower()
    local talker = data.talker or "Desconocido"
    local text = data.text or ""

    -- Map GMCP channel name to our keys
    local channel_key = M.map_gmcp_channel(channel_name)

    -- Format message
    local formatted = talker .. ": " .. text

    -- Handle as normal message
    M.on_message(channel_key, formatted)
end

-- Map GMCP channel names to internal keys.
-- Bugfix (Phase 7C audit): non-ASCII identifiers ("telepátia", "ciudadanía")
-- are NOT valid Lua identifiers in Lua 5.4+ — they must be expressed as
-- bracketed string keys.
function M.map_gmcp_channel(gmcp_name)
    local map = {
        bando        = "bando",
        ["telepátia"] = "telepathy",
        telepathy    = "telepathy",
        sala         = "sala",
        gremio       = "gremio",
        familia      = "familia",
        rol          = "rol",
        ciudad       = "ciudadania",
        ["ciudadanía"] = "ciudadania",
        chat         = "chat",
        eventos      = "eventos",
        sistema      = "sistema",
        especial     = "especial",
        general      = "sala",
    }
    return map[gmcp_name] or "sala"
end

-- Add message to channel history
function M.add_to_history(channel_key, text)
    local channel = CHANNELS[channel_key]
    if not channel then
        return
    end

    -- Add message with timestamp
    local msg_entry = {
        time = os.date("%H:%M:%S"),
        text = text,
    }

    table.insert(channel.history, msg_entry)

    -- Trim to max 99 messages (VipMud standard)
    if #channel.history > MAX_HISTORY_PER_CHANNEL then
        table.remove(channel.history, 1)
    end
end

-- Get message history for channel
function M.get_history(channel_key)
    local channel = CHANNELS[channel_key]
    if not channel then
        return {}
    end
    return channel.history
end

-- Get history as formatted string (for display)
function M.get_history_string(channel_key)
    local history = M.get_history(channel_key)
    local lines = {}
    for _, msg in ipairs(history) do
        table.insert(lines, "[" .. msg.time .. "] " .. msg.text)
    end
    return table.concat(lines, "\n")
end

-- Clear history for channel
function M.clear_history(channel_key)
    local channel = CHANNELS[channel_key]
    if channel then
        channel.history = {}
    end
end

-- Get total message count in all channels
function M.get_total_message_count()
    local count = 0
    for _, channel in pairs(CHANNELS) do
        count = count + #channel.history
    end
    return count
end

-- Mute/unmute channels
function M.set_muted(channel_key, muted)
    local channel = CHANNELS[channel_key]
    if channel then
        channel.muted = muted
        local status = muted and "muted" or "unmuted"
        vipzhyla.say("[COMUNICACIONES] Channel " .. channel.name .. " " .. status)
    end
end

function M.is_muted(channel_key)
    local channel = CHANNELS[channel_key]
    return channel and channel.muted or false
end

function M.toggle_muted(channel_key)
    local channel = CHANNELS[channel_key]
    if channel then
        M.set_muted(channel_key, not channel.muted)
    end
end

-- Mute/unmute all channels
function M.mute_all()
    for channel_key, _ in pairs(CHANNELS) do
        M.set_muted(channel_key, true)
    end
end

function M.unmute_all()
    for channel_key, _ in pairs(CHANNELS) do
        M.set_muted(channel_key, false)
    end
end

-- Get channel status
function M.get_status()
    local status = {}
    for key, channel in pairs(CHANNELS) do
        status[key] = {
            name = channel.name,
            muted = channel.muted,
            message_count = #channel.history,
        }
    end
    return status
end

-- Get list of all channels
function M.get_channels()
    local channels = {}
    for key, channel in pairs(CHANNELS) do
        table.insert(channels, {
            key = key,
            name = channel.name,
            muted = channel.muted,
        })
    end
    return channels
end

return M

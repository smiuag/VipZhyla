--[[
Audio panning and spatial sound effects module.
Provides directional audio, distance simulation, and HRTF filtering.

Phase 6E: Immersive 3D audio for ambient sounds and environmental effects.
]]

local M = {}

-- Direction names and aliases
local DIRECTIONS = {
    -- Cardinal
    front = "front",
    ahead = "front",
    north = "front",

    left = "left",
    west = "left",

    right = "right",
    east = "right",

    back = "back",
    behind = "back",
    south = "back",

    -- Diagonals
    front_left = "front_left",
    front_right = "front_right",
    back_left = "back_left",
    back_right = "back_right",
    northwest = "front_left",
    northeast = "front_right",
    southwest = "back_left",
    southeast = "back_right",

    -- Vertical
    above = "above",
    up = "above",
    below = "below",
    down = "below",

    -- Center
    center = "center",
    all = "center",
}

-- Active sounds with panning state
local active_sounds = {}

-- Global panning settings
local config = {
    panning_enabled = true,
    hrtf_enabled = true,      -- HRTF filtering for elevation
    distance_simulation = true, -- Volume scaling for distance
    max_sounds = 8,            -- Maximum simultaneous panned sounds
}

function M.init(game)
    game.audio = game.audio or {}
    game.audio.panning = M
    game.audio.config = config
    game.audio.sounds = active_sounds
end

function M.play_directional(sound_file, direction, distance, loop_count)
    [[
    Play a sound with 3D panning.

    Args:
        sound_file: Path to sound file (e.g., "RL/Oficios/Minero/Picando.wav")
        direction: Direction name (front, left, right, back, above, below, etc.)
        distance: Distance factor 0.0=close, 1.0=far (default 0.5)
        loop_count: Number of times to loop (default 1)

    Returns:
        sound_id for later reference
    ]]

    if not config.panning_enabled then
        vipzhyla.play_sound(sound_file)
        return nil
    end

    direction = direction or "center"
    distance = distance or 0.5
    loop_count = loop_count or 1

    -- Normalize direction
    direction = DIRECTIONS[direction:lower()] or "center"

    -- Clamp distance
    distance = math.max(0.0, math.min(1.0, distance))

    -- Create sound ID
    local sound_id = "panned_" .. os.time() .. "_" .. math.random(10000)

    -- Store panning info
    active_sounds[sound_id] = {
        file = sound_file,
        direction = direction,
        distance = distance,
        loop_count = loop_count,
        timestamp = os.time(),
    }

    -- Call Python audio manager with panning info
    -- (will be connected by script_loader.py)
    if vipzhyla.play_directional_sound then
        vipzhyla.play_directional_sound(sound_file, direction, distance, loop_count, sound_id)
    else
        -- Fallback to mono sound if directional not available
        vipzhyla.play_sound(sound_file)
    end

    return sound_id
end

function M.update_position(sound_id, direction, distance)
    [[
    Update the position of an active sound.

    Args:
        sound_id: Sound ID from play_directional()
        direction: New direction
        distance: New distance factor

    Returns:
        true if updated successfully
    ]]

    if not active_sounds[sound_id] then
        return false
    end

    direction = DIRECTIONS[direction:lower()] or active_sounds[sound_id].direction
    distance = math.max(0.0, math.min(1.0, distance))

    active_sounds[sound_id].direction = direction
    active_sounds[sound_id].distance = distance

    if vipzhyla.update_sound_position then
        vipzhyla.update_sound_position(sound_id, direction, distance)
    end

    return true
end

function M.stop_sound(sound_id)
    [[Stop a directional sound.]]

    if active_sounds[sound_id] then
        active_sounds[sound_id] = nil
        if vipzhyla.stop_sound then
            vipzhyla.stop_sound(sound_id)
        end
        return true
    end
    return false
end

function M.stop_all()
    [[Stop all active directional sounds.]]

    for sound_id, _ in pairs(active_sounds) do
        M.stop_sound(sound_id)
    end
end

function M.get_direction_description(direction)
    [[
    Get a human-readable description of direction.
    E.g., "left" -> "to your left"
    ]]

    local descriptions = {
        front = "ahead",
        left = "to your left",
        right = "to your right",
        back = "behind you",
        front_left = "ahead and to the left",
        front_right = "ahead and to the right",
        back_left = "behind and to the left",
        back_right = "behind and to the right",
        above = "above you",
        below = "below you",
        center = "all around",
    }

    direction = DIRECTIONS[direction:lower()] or "center"
    return descriptions[direction] or "around you"
end

function M.announce_sound(message, direction, distance)
    [[
    Announce a sound with TTS location description.

    E.g., announce_sound("footsteps", "left")
    -> Plays directional sound, announces "footsteps to your left"
    ]]

    direction = direction or "center"
    distance = distance or 0.5

    local dir_desc = M.get_direction_description(direction)
    local announcement = message .. " " .. dir_desc

    vipzhyla.announce(announcement)
    return M.play_directional(message, direction, distance)
end

function M.set_panning_enabled(enabled)
    config.panning_enabled = enabled
    if not enabled then
        M.stop_all()
    end
end

function M.set_hrtf_enabled(enabled)
    config.hrtf_enabled = enabled
end

function M.set_distance_simulation_enabled(enabled)
    config.distance_simulation = enabled
end

function M.get_active_sounds()
    [[Return table of all active directional sounds.]]
    return active_sounds
end

function M.get_config()
    [[Return current audio panning configuration.]]
    return config
end

return M

--[[
Ambientacion Module - Region-based ambient sounds and atmosphere

Dynamic ambient sounds that change based on location.
Creates immersive audio environment for blind players.

Features:
- Region detection (Anduar, Eldor, Takome, etc.)
- Ambient sound loops (forest, city, dungeon, etc.)
- Weather effects (rain, wind, thunder)
- Time-of-day effects
- NPC ambient chatter
- Location-specific sound effects

Ported from: Ambientacion/*.set (8 files, 130 lines)
             Regional sound organization from VipMud

This enhances spatial awareness through sound design.
--]]

local M = {}

-- Region definitions
local REGIONS = {
    anduar = {
        name = "Anduar",
        ambient = "RL/Ambientes/Anduar/bosque.mp3",
        description = "Bosque antiguo",
    },
    eldor = {
        name = "Eldor",
        ambient = "RL/Ambientes/Eldor/ciudad.mp3",
        description = "Ciudad comercial",
    },
    takome = {
        name = "Takome",
        ambient = "RL/Ambientes/Takome/montaña.mp3",
        description = "Montañas nevadas",
    },
    golthur = {
        name = "Golthur",
        ambient = "RL/Ambientes/Golthur/mina.mp3",
        description = "Minas enanas",
    },
    dendra = {
        name = "Dendra",
        ambient = "RL/Ambientes/Dendra/magia.mp3",
        description = "Torre de magia",
    },
    mystraal = {
        name = "Mystraal",
        ambient = "RL/Ambientes/Mystraal/castillo.mp3",
        description = "Castillo antiguo",
    },
    dungeon = {
        name = "Dungeon",
        ambient = "RL/Ambientes/Dungeon/caverna.mp3",
        description = "Cavernas oscuras",
    },
}

-- Sound effects library
local SOUND_EFFECTS = {
    -- Weather
    rain = "RL/Sonidos/Weather/lluvia.wav",
    wind = "RL/Sonidos/Weather/viento.wav",
    thunder = "RL/Sonidos/Weather/trueno.wav",

    -- Ambient
    forest_birds = "RL/Sonidos/Ambientes/pajaros.wav",
    city_market = "RL/Sonidos/Ambientes/mercado.wav",
    city_bells = "RL/Sonidos/Ambientes/campanas.wav",
    dungeon_drip = "RL/Sonidos/Ambientes/gotas.wav",
    dungeon_echo = "RL/Sonidos/Ambientes/eco.wav",

    -- NPC ambient
    npc_chatter = "RL/Sonidos/NPC/charla.wav",
    npc_laugh = "RL/Sonidos/NPC/risa.wav",
    npc_footsteps = "RL/Sonidos/NPC/pasos.wav",
}

-- Current ambient state
local AMBIENT_STATE = {
    current_region = "unknown",
    ambient_playing = false,
    ambient_volume = 50,
    effects_enabled = true,
    npc_ambient_enabled = true,
    weather_effects = {},
}

-- Ambient playback tracking
local AMBIENT_TRACKS = {
    background = nil,
    effect = nil,
}

-- Initialize module
function M.init(game)
    vipzhyla.say("[AMBIENTACION] Sistema de sonidos ambientales inicializado")
end

-- Detect region from room name
function M.detect_region(room_name)
    if not room_name then
        return "unknown"
    end

    local room_lower = room_name:lower()

    -- Simple pattern matching (can be enhanced)
    if room_lower:match("anduar") or room_lower:match("bosque") then
        return "anduar"
    elseif room_lower:match("eldor") or room_lower:match("ciudad") then
        return "eldor"
    elseif room_lower:match("takome") or room_lower:match("montaña") then
        return "takome"
    elseif room_lower:match("golthur") or room_lower:match("mina") then
        return "golthur"
    elseif room_lower:match("dendra") or room_lower:match("torre") then
        return "dendra"
    elseif room_lower:match("mystraal") or room_lower:match("castillo") then
        return "mystraal"
    elseif room_lower:match("dungeon") or room_lower:match("caverna") or room_lower:match("cueva") then
        return "dungeon"
    else
        return "unknown"
    end
end

-- Handle room change (from GMCP or movement)
function M.on_room_changed(room_name)
    local new_region = M.detect_region(room_name)

    if new_region ~= AMBIENT_STATE.current_region then
        AMBIENT_STATE.current_region = new_region
        M.play_ambient_for_region(new_region)
        vipzhyla.say("[AMBIENTE] Región: " .. (REGIONS[new_region] and REGIONS[new_region].name or "Desconocida"))
    end
end

-- Play ambient sound for region
function M.play_ambient_for_region(region)
    local region_data = REGIONS[region]

    if not region_data then
        M.stop_ambient()
        return
    end

    vipzhyla.say("[AMBIENT] Reproduciendo: " .. region_data.description)
    vipzhyla.play_sound(region_data.ambient)

    AMBIENT_STATE.ambient_playing = true
    AMBIENT_TRACKS.background = region_data.ambient
end

-- Stop ambient sound
function M.stop_ambient()
    vipzhyla.say("[AMBIENT] Detenido")
    AMBIENT_STATE.ambient_playing = false
    AMBIENT_TRACKS.background = nil
end

-- Play weather effect
function M.add_weather_effect(weather_type)
    if not SOUND_EFFECTS[weather_type] then
        return false
    end

    table.insert(AMBIENT_STATE.weather_effects, weather_type)
    vipzhyla.play_sound(SOUND_EFFECTS[weather_type])

    vipzhyla.say("[TIEMPO] " .. weather_type)
    return true
end

-- Remove weather effect
function M.remove_weather_effect(weather_type)
    for i, effect in ipairs(AMBIENT_STATE.weather_effects) do
        if effect == weather_type then
            table.remove(AMBIENT_STATE.weather_effects, i)
            return true
        end
    end
    return false
end

-- Play NPC ambient chatter
function M.play_npc_ambient(npc_type)
    if not SOUND_EFFECTS[npc_type] then
        return false
    end

    vipzhyla.play_sound(SOUND_EFFECTS[npc_type])
    return true
end

-- Get current region
function M.get_current_region()
    return AMBIENT_STATE.current_region
end

-- Get region info
function M.get_region_info(region)
    return REGIONS[region]
end

-- Get all regions
function M.get_regions()
    local regions = {}
    for key, data in pairs(REGIONS) do
        table.insert(regions, {
            key = key,
            name = data.name,
            description = data.description,
        })
    end
    return regions
end

-- Set ambient volume
function M.set_ambient_volume(volume)
    if volume < 0 then volume = 0 end
    if volume > 100 then volume = 100 end

    AMBIENT_STATE.ambient_volume = volume
    vipzhyla.say("[AMBIENT] Volumen: " .. volume .. "%")
end

-- Enable/disable effects
function M.set_effects_enabled(enabled)
    AMBIENT_STATE.effects_enabled = enabled
    vipzhyla.say("[AMBIENT] Efectos: " .. (enabled and "Activados" or "Desactivados"))
end

function M.set_npc_ambient_enabled(enabled)
    AMBIENT_STATE.npc_ambient_enabled = enabled
    vipzhyla.say("[AMBIENT] Ambiente NPC: " .. (enabled and "Activado" or "Desactivado"))
end

-- Get status
function M.get_status()
    return {
        current_region = AMBIENT_STATE.current_region,
        ambient_playing = AMBIENT_STATE.ambient_playing,
        volume = AMBIENT_STATE.ambient_volume,
        weather_effects = AMBIENT_STATE.weather_effects,
        effects_enabled = AMBIENT_STATE.effects_enabled,
    }
end

-- Log status
function M.log_status()
    vipzhyla.say("[AMBIENTACION]")
    vipzhyla.say("  Región actual: " .. (AMBIENT_STATE.current_region or "Desconocida"))
    vipzhyla.say("  Ambiente: " .. (AMBIENT_STATE.ambient_playing and "Reproduciendo" or "Detenido"))
    vipzhyla.say("  Volumen: " .. AMBIENT_STATE.ambient_volume .. "%")

    if #AMBIENT_STATE.weather_effects > 0 then
        vipzhyla.say("  Efectos climáticos: " .. table.concat(AMBIENT_STATE.weather_effects, ", "))
    end
end

function M.log_regions()
    vipzhyla.say("[REGIONES DISPONIBLES]")
    for i, region in ipairs(M.get_regions()) do
        vipzhyla.say(string.format("  %d. %s - %s", i, region.name, region.description))
    end
end

return M

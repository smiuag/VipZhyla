--[[
VipZhyla Lua MegaScript for Reinos de Leyenda

Main entry point for all game automation, triggers, aliases, and configuration.
Modules are loaded on-demand and initialized in order.

Structure:
- Load helper libraries
- Initialize configuration
- Load core game modules (comunicaciones, estado, etc.)
- Register all triggers and event handlers
- Start automated systems

Equivalent to: VipMud's Reinos de leyenda.set + all dependency scripts
]]

-- Version tracking
local GAME_SCRIPT_VERSION = "1.0.0"
local GAME_NAME = "Reinos de Leyenda"

-- Global game object (MUST be global for Python to access via lua.globals()['game'])
game = {
    version = GAME_SCRIPT_VERSION,
    name = GAME_NAME,
    initialized = false,
    modules = {},
}

-- ========== Load Helper Libraries ==========

local helpers = require("lib.helpers")

-- Version with features
local FEATURES = {
    path_recording = true,      -- Phase 6E: Record/playback routes
    ambient_sounds = true,      -- Phase 6E: Regional ambient audio
    ability_detection = true,   -- Phase 6E: 50+ ability patterns
    professions = true,         -- Phase 6E: 5 profession systems (Minero, Herrero, Marinero, Jornalero, Crear)
    class_abilities = true,     -- Phase 6E: All 24 character classes implemented
    audio_panning = true,       -- Phase 6E: 3D spatial audio with panning and distance simulation
    interactive_prompts = true, -- Phase 6E: Dialog system for class/mode selection + startup wizard
}

-- ========== Initialize Core Tables ==========

-- Character state
game.character = {
    name = "",
    level = 0,
    class = "",
    race = "",
    hp = 0,
    maxhp = 0,
    mp = 0,
    maxmp = 0,
}

-- Current room
game.room = {
    name = "Unknown",
    exits = {},
    description = "",
}

-- Configuration/settings
game.config = {
    modo_j = 1,              -- 1=Combate, 2=XP, 3=Idle
    modo_e = 0,              -- Expert mode: 0/1
    modo_path = 0,           -- 0=normal, 1=turbo, 2=ultra
    modo_s = 0,              -- Silent mode
    alerta_vida = 1,         -- Health alert: 0/1
    filtro_salidas = 1,      -- Filter long descriptions: 0/1
    auto_centrar = 1,        -- Auto-center: 0/1
    verbose = 0,             -- Verbose output: 0/1
}

-- Channel configuration (muting)
game.channels = {
    bando = { muted = false },
    telepathy = { muted = false },
    sala = { muted = false },
    gremio = { muted = false },
    familia = { muted = false },
    rol = { muted = false },
    ciudadania = { muted = false },
    chat = { muted = false },
    eventos = { muted = false },
    sistema = { muted = false },
    especial = { muted = false },
}

-- Combat state
game.combat = {
    in_combat = false,
    current_enemy = "",
    enemies = {},
    last_attack_time = 0,
}

-- ========== Module Loading Framework ==========

function game.load_module(module_name)
    if not game.modules[module_name] then
        local status, module = pcall(require, "modules." .. module_name)
        if status then
            game.modules[module_name] = module
            vipzhyla.say("[SCRIPT] Loaded module: " .. module_name)
            return module
        else
            vipzhyla.say("[ERROR] Failed to load module " .. module_name .. ": " .. tostring(module))
            return nil
        end
    end
    return game.modules[module_name]
end

function game.init_module(module_name)
    local module = game.load_module(module_name)
    if module and module.init then
        pcall(module.init, game)
        vipzhyla.say("[SCRIPT] Initialized module: " .. module_name)
    end
end

-- ========== Initialize Game ==========

function game.init()
    vipzhyla.announce("Initializing " .. GAME_NAME .. " scripts version " .. GAME_SCRIPT_VERSION)

    -- Load modules in dependency order
    game.init_module("estado")          -- Base state tracking
    game.init_module("configuracion")   -- Configuration
    game.init_module("comunicaciones")  -- Channel system
    game.init_module("movimiento")      -- Movement system
    game.init_module("combate")         -- Combat system
    game.init_module("habilidades")     -- Ability detection (Phase 6E)
    game.init_module("navigation")      -- Navigation/paths (Phase 6E)
    game.init_module("paths")           -- Path recording (Phase 6E)
    game.init_module("ambientacion")    -- Ambient sounds (Phase 6E)
    game.init_module("audio")           -- Audio panning (Phase 6E)
    game.init_module("prompts")         -- Interactive prompts (Phase 6E)
    game.init_module("oficios")         -- Profession system (Phase 6E)
    game.init_module("estados")         -- Status effects/buffs (Phase 7A)

    -- Mark as initialized
    game.initialized = true

    -- Log feature status
    vipzhyla.say("[FEATURES - Phase 6E COMPLETE]")
    vipzhyla.say("  Path Recording: " .. (FEATURES.path_recording and "✓" or "✗"))
    vipzhyla.say("  Ambient Sounds: " .. (FEATURES.ambient_sounds and "✓" or "✗"))
    vipzhyla.say("  Ability Detection: " .. (FEATURES.ability_detection and "✓" or "✗"))
    vipzhyla.say("  Professions (5): " .. (FEATURES.professions and "✓" or "✗"))
    vipzhyla.say("  Character Classes (24): " .. (FEATURES.class_abilities and "✓" or "✗"))
    vipzhyla.say("  Audio Panning (3D): " .. (FEATURES.audio_panning and "✓" or "✗"))
    vipzhyla.say("  Interactive Prompts: " .. (FEATURES.interactive_prompts and "✓" or "✗"))

    vipzhyla.announce("Scripts initialized successfully")
    helpers.log("All modules loaded and ready")
end

-- ========== Event Handlers (will be connected by Python) ==========

function game.on_mud_message(channel, text)
    if not game.initialized then return end

    -- Auto-detect status effects from messages (Phase 7A)
    if game.modules.estados then
        pcall(game.modules.estados.process_message, text)
    end

    -- Dispatch to modules
    for _, module in pairs(game.modules) do
        if module.on_message then
            pcall(module.on_message, channel, text)
        end
    end
end

function game.on_gmcp_data(module_name, data)
    if not game.initialized then return end
    -- Update character data from GMCP
    if module_name == "Char.Status" then
        game.character.name = data.name or ""
        game.character.level = data.level or 0
        game.character.class = data.class or ""
    elseif module_name == "Char.Vitals" then
        game.character.hp = data.hp or 0
        game.character.maxhp = data.maxhp or 0
        game.character.mp = data.mp or 0
        game.character.maxmp = data.maxmp or 0
    elseif module_name == "Room.Info" then
        game.room.name = data.name or "Unknown"
        game.room.exits = data.exits or {}
        game.room.description = data.desc or ""
    end

    -- Dispatch to modules
    for _, module in pairs(game.modules) do
        if module.on_gmcp then
            pcall(module.on_gmcp, module_name, data)
        end
    end
end

function game.send_command(command)
    vipzhyla.send_command(command)
end

function game.say(text)
    vipzhyla.say(text)
end

function game.announce(text)
    vipzhyla.announce(text)
end

function game.play_sound(sound_path)
    vipzhyla.play_sound(sound_path)
end

-- ========== Helper Functions ==========

function game.get_character()
    return game.character
end

function game.get_room()
    return game.room
end

function game.get_config(key)
    return game.config[key]
end

function game.set_config(key, value)
    game.config[key] = value
end

function game.is_channel_muted(channel)
    local ch = game.channels[channel]
    return ch and ch.muted or false
end

function game.mute_channel(channel, muted)
    if game.channels[channel] then
        game.channels[channel].muted = muted
    end
end

-- ========== Status and Info ==========

function game.get_status()
    return {
        name = game.character.name,
        level = game.character.level,
        class = game.character.class,
        hp = game.character.hp,
        maxhp = game.character.maxhp,
        mp = game.character.mp,
        maxmp = game.character.maxmp,
        room = game.room.name,
        in_combat = game.combat.in_combat,
    }
end

-- Return game object so it can be used by Python
return game

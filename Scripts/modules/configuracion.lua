--[[
Configuracion Module - Game configuration and settings

Manages:
- Game mode settings (ModoJ, ModoE, ModoPath, ModoS)
- Preferences (AlertaVida, FiltroSalidas, AutoCentrar)
- Runtime configuration modification
- Persistence to JSON

Ported from: Configuracion.set

Modes:
- ModoJ: 1=Combate, 2=XP, 3=Idle (affects automation priority)
- ModoE: Expert mode 0/1 (affects verbosity)
- ModoPath: 0=normal, 1=turbo, 2=ultra (affects travel speed/spam)
- ModoS: Silent mode 0/1 (affects TTS)

Preferences:
- AlertaVida: Health alerts 0/1
- FiltroSalidas: Filter long descriptions 0/1
- AutoCentrar: Auto-center on room changes 0/1
--]]

local M = {}

-- Default configuration
local CONFIG = {
    -- Game modes
    modo_j = 1,              -- 1=Combate, 2=XP, 3=Idle
    modo_e = 0,              -- Expert mode: 0/1
    modo_path = 0,           -- 0=normal, 1=turbo, 2=ultra
    modo_s = 0,              -- Silent mode: 0/1

    -- Preferences
    alerta_vida = 1,         -- Health alerts: 0/1
    filtro_salidas = 1,      -- Filter descriptions: 0/1
    auto_centrar = 1,        -- Auto-center: 0/1

    -- Other settings
    verbose = 0,             -- Verbose output: 0/1
    debug = 0,               -- Debug mode: 0/1
}

-- Mode descriptions (for UI)
local MODE_DESCRIPTIONS = {
    modo_j = {
        "Modo Combate (Prioridad: ataque, defensa, magia)",
        "Modo XP (Prioridad: experiencia, aventura, nivel)",
        "Modo Idle (Prioridad: inactividad, espera, AFK)",
    },
    modo_e = {
        "Modo Normal (Mensajes descriptivos, mucho spam)",
        "Modo Experto (Mensajes concisos, sin repeticiones)",
    },
    modo_path = {
        "Modo Normal (Descripciones completas de rooms)",
        "Modo Turbo (Descripciones filtradas, movimiento rápido)",
        "Modo Ultra (Sin descripciones, máxima velocidad)",
    },
}

-- Initialize configuration
function M.init(game)
    vipzhyla.say("[CONFIGURACION] Initializing configuration system")

    -- In production, load from JSON config file here
    -- For now, use defaults
    M.log_modes()

    vipzhyla.announce("Sistema de configuración listo")
end

-- Get configuration value
function M.get(key)
    return CONFIG[key]
end

-- Set configuration value
function M.set(key, value)
    if CONFIG[key] ~= nil then
        CONFIG[key] = value
        vipzhyla.say("[CONFIG] " .. key .. " = " .. tostring(value))
        return true
    else
        vipzhyla.say("[CONFIG ERROR] Unknown config key: " .. key)
        return false
    end
end

-- Get all configuration as table
function M.get_all()
    return CONFIG
end

-- Reset to defaults
function M.reset_defaults()
    CONFIG.modo_j = 1
    CONFIG.modo_e = 0
    CONFIG.modo_path = 0
    CONFIG.modo_s = 0
    CONFIG.alerta_vida = 1
    CONFIG.filtro_salidas = 1
    CONFIG.auto_centrar = 1
    CONFIG.verbose = 0
    CONFIG.debug = 0

    vipzhyla.say("[CONFIG] Reset to defaults")
end

-- ===== Mode-specific getters =====

function M.get_modo_j()
    return CONFIG.modo_j
end

function M.set_modo_j(value)
    if value >= 1 and value <= 3 then
        CONFIG.modo_j = value
        local modes = { "Combate", "XP", "Idle" }
        vipzhyla.announce("Modo de juego: " .. modes[value])
        return true
    end
    return false
end

function M.get_modo_e()
    return CONFIG.modo_e == 1
end

function M.set_modo_e(enabled)
    CONFIG.modo_e = enabled and 1 or 0
    local status = enabled and "Experto" or "Normal"
    vipzhyla.announce("Modo: " .. status)
    return true
end

function M.get_modo_path()
    return CONFIG.modo_path
end

function M.set_modo_path(value)
    if value >= 0 and value <= 2 then
        CONFIG.modo_path = value
        local modes = { "Normal", "Turbo", "Ultra" }
        vipzhyla.announce("Velocidad de viaje: " .. modes[value + 1])
        return true
    end
    return false
end

function M.get_modo_s()
    return CONFIG.modo_s == 1
end

function M.set_modo_s(enabled)
    CONFIG.modo_s = enabled and 1 or 0
    local status = enabled and "SILENCIO" or "Normal"
    vipzhyla.announce("Modo de sonido: " .. status)
    return true
end

-- ===== Preference getters/setters =====

function M.is_health_alert_enabled()
    return CONFIG.alerta_vida == 1
end

function M.set_health_alert(enabled)
    CONFIG.alerta_vida = enabled and 1 or 0
    vipzhyla.say("[CONFIG] Alertas de vida " .. (enabled and "activadas" or "desactivadas"))
end

function M.is_description_filter_enabled()
    return CONFIG.filtro_salidas == 1
end

function M.set_description_filter(enabled)
    CONFIG.filtro_salidas = enabled and 1 or 0
    vipzhyla.say("[CONFIG] Filtro de descripciones " .. (enabled and "activado" or "desactivado"))
end

function M.is_auto_center_enabled()
    return CONFIG.auto_centrar == 1
end

function M.set_auto_center(enabled)
    CONFIG.auto_centrar = enabled and 1 or 0
    vipzhyla.say("[CONFIG] Auto-centrado " .. (enabled and "activado" or "desactivado"))
end

-- ===== Logging/Display =====

function M.log_modes()
    local modes = { "Combate", "XP", "Idle" }
    local expert = CONFIG.modo_e == 1 and "Experto" or "Normal"
    local path_modes = { "Normal", "Turbo", "Ultra" }
    local silent = CONFIG.modo_s == 1 and "SILENCIO" or "Normal"

    vipzhyla.say("[MODOS]")
    vipzhyla.say("  ModoJ: " .. modes[CONFIG.modo_j] .. " (juego)")
    vipzhyla.say("  ModoE: " .. expert .. " (experiencia)")
    vipzhyla.say("  ModoPath: " .. path_modes[CONFIG.modo_path + 1] .. " (viaje)")
    vipzhyla.say("  ModoS: " .. silent .. " (sonido)")
end

function M.log_prefs()
    local health = CONFIG.alerta_vida == 1 and "ON" or "OFF"
    local filter = CONFIG.filtro_salidas == 1 and "ON" or "OFF"
    local center = CONFIG.auto_centrar == 1 and "ON" or "OFF"

    vipzhyla.say("[PREFERENCIAS]")
    vipzhyla.say("  AlertaVida: " .. health)
    vipzhyla.say("  FiltroSalidas: " .. filter)
    vipzhyla.say("  AutoCentrar: " .. center)
end

-- Log all configuration
function M.log_all()
    vipzhyla.say("[CONFIG ACTUAL]")
    for key, value in pairs(CONFIG) do
        vipzhyla.say("  " .. key .. " = " .. tostring(value))
    end
end

-- Save configuration to JSON (will be implemented in Python)
function M.save_config()
    vipzhyla.say("[CONFIG] Saving configuration to file...")
    -- Python side will handle persistence
end

-- Load configuration from JSON (will be implemented in Python)
function M.load_config()
    vipzhyla.say("[CONFIG] Loading configuration from file...")
    -- Python side will handle loading
end

return M

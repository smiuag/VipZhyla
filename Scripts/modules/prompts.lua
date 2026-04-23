--[[
Interactive prompts module for character setup and game configuration.
Provides dialogs for class selection, game mode configuration, and preferences.

Phase 6E: Interactive UI for initial character setup and settings management.
]]

local M = {}

-- Dialog state
local dialog_state = {
    active = false,
    current_dialog = nil,
    result = nil,
}

function M.init(game)
    game.prompts = game.prompts or {}
    game.prompts.dialog_state = dialog_state
end

--[[ ===== Class Selection Dialog ===== ]]

function M.prompt_class_selection()
    [[
    Show dialog to select character class.
    Returns: class name (string) or nil if cancelled
    ]]

    local classes = {
        "Soldado", "Mago", "Clérigo", "Druida", "Bardo",
        "Asesino", "Ranger", "Monje", "Nigromante", "Templario",
        "Hechicero", "Brujo", "Alquimista", "Cazador de Dragones",
        "Ermitaño", "Trovador", "Corsario", "Espadachín", "Caballero Oscuro",
        "Paladín", "Khazad"
    }

    return M._show_list_dialog("Selecciona tu Clase", "Clases Disponibles:", classes, "Aceptar", "Cancelar")
end

--[[ ===== Game Mode Configuration ===== ]]

function M.prompt_combat_mode()
    [[
    Show dialog to select combat mode.
    Returns: mode number (1=Combat, 2=XP, 3=Idle) or nil if cancelled
    ]]

    local modes = {
        "Combate (Combate activo)",
        "XP (Ganar experiencia)",
        "Idle (Ocio)"
    }

    local result = M._show_list_dialog("Modo de Combate", "Selecciona el modo:", modes, "Aceptar", "Cancelar")
    if result == modes[1] then return 1
    elseif result == modes[2] then return 2
    elseif result == modes[3] then return 3
    else return nil end
end

function M.prompt_travel_speed()
    [[
    Show dialog to select travel speed mode.
    Returns: mode number (0=Normal, 1=Turbo, 2=Ultra) or nil if cancelled
    ]]

    local modes = {
        "Normal (Velocidad normal)",
        "Turbo (1.5x velocidad)",
        "Ultra (2x velocidad)"
    }

    local result = M._show_list_dialog("Velocidad de Viaje", "Selecciona la velocidad:", modes, "Aceptar", "Cancelar")
    if result == modes[1] then return 0
    elseif result == modes[2] then return 1
    elseif result == modes[3] then return 2
    else return nil end
end

function M.prompt_expert_mode()
    [[
    Show yes/no dialog for expert mode.
    Returns: 1 (expert) or 0 (normal) or nil if cancelled
    ]]

    return M._show_yes_no_dialog("Modo Experto", "¿Activar modo experto?\n\n(Oculta mensajes de ayuda)")
end

function M.prompt_silent_mode()
    [[
    Show yes/no dialog for silent mode.
    Returns: 1 (silent) or 0 (normal) or nil if cancelled
    ]]

    return M._show_yes_no_dialog("Modo Silencioso", "¿Activar modo silencioso?\n\n(Desactiva avisos de sonido)")
end

--[[ ===== Audio Configuration ===== ]]

function M.prompt_audio_options()
    [[
    Show dialog for audio configuration options.
    Returns: table with selected options or nil if cancelled
    ]]

    local options = {
        "Panning 3D activado",
        "HRTF activado",
        "Simulación de distancia activada"
    }

    return M._show_multi_select_dialog("Opciones de Audio", "Selecciona opciones:", options, "Aceptar", "Cancelar")
end

function M.prompt_verbosity_level()
    [[
    Show dialog to select TTS verbosity level.
    Returns: level name (string) or nil if cancelled
    ]]

    local levels = {
        "Silencioso",
        "Mínimo",
        "Normal",
        "Verboso",
        "Debug"
    }

    return M._show_list_dialog("Nivel de Verbosidad", "Selecciona nivel de TTS:", levels, "Aceptar", "Cancelar")
end

--[[ ===== Preferences Dialog ===== ]]

function M.prompt_preferences()
    [[
    Show comprehensive preferences dialog.
    Returns: table with preference settings or nil if cancelled
    ]]

    local prefs = {
        alerta_vida = M._show_yes_no_dialog("Alerta de Vida", "¿Activar alertas de vida baja?"),
        filtro_salidas = M._show_yes_no_dialog("Filtro de Salidas", "¿Filtrar descripciones largas?"),
        auto_centrar = M._show_yes_no_dialog("Auto-centrar", "¿Centrar automáticamente en combate?"),
    }

    -- If any dialog was cancelled, return nil
    if prefs.alerta_vida == nil or prefs.filtro_salidas == nil or prefs.auto_centrar == nil then
        return nil
    end

    return prefs
end

--[[ ===== Internal Helpers ===== ]]

function M._show_list_dialog(title, message, items, ok_label, cancel_label)
    [[
    Show a list selection dialog.

    Args:
        title: Dialog title
        message: Prompt message
        items: List of selectable items
        ok_label: OK button label
        cancel_label: Cancel button label

    Returns:
        Selected item (string) or nil if cancelled
    ]]

    if not vipzhyla.show_list_dialog then
        return items[1]  -- Fallback to first item if UI unavailable
    end

    return vipzhyla.show_list_dialog(title, message, items, ok_label, cancel_label)
end

function M._show_yes_no_dialog(title, message)
    [[
    Show a yes/no confirmation dialog.

    Args:
        title: Dialog title
        message: Prompt message

    Returns:
        1 (yes), 0 (no), or nil if cancelled
    ]]

    if not vipzhyla.show_yes_no_dialog then
        return 1  -- Fallback to 'yes' if UI unavailable
    end

    return vipzhyla.show_yes_no_dialog(title, message)
end

function M._show_text_dialog(title, message, default_value)
    [[
    Show a text input dialog.

    Args:
        title: Dialog title
        message: Prompt message
        default_value: Default text value

    Returns:
        Entered text (string) or nil if cancelled
    ]]

    if not vipzhyla.show_text_dialog then
        return default_value  -- Fallback to default if UI unavailable
    end

    return vipzhyla.show_text_dialog(title, message, default_value)
end

function M._show_multi_select_dialog(title, message, items, ok_label, cancel_label)
    [[
    Show a multi-selection dialog (checkboxes).

    Args:
        title: Dialog title
        message: Prompt message
        items: List of selectable items
        ok_label: OK button label
        cancel_label: Cancel button label

    Returns:
        Table of selected items (indices) or nil if cancelled
    ]]

    if not vipzhyla.show_multi_select_dialog then
        return items  -- Fallback to all items if UI unavailable
    end

    return vipzhyla.show_multi_select_dialog(title, message, items, ok_label, cancel_label)
end

--[[ ===== Startup Wizard ===== ]]

function M.run_startup_wizard()
    [[
    Run the complete startup wizard for new characters.
    Prompts for class, game modes, audio options, and preferences.

    Returns:
        Table with complete character configuration or nil if cancelled
    ]]

    local config = {}

    -- Step 1: Class Selection
    vipzhyla.announce("Paso 1: Selecciona tu clase")
    config.class = M.prompt_class_selection()
    if not config.class then
        return nil  -- User cancelled
    end
    vipzhyla.announce("Clase seleccionada: " .. config.class)

    -- Step 2: Combat Mode
    vipzhyla.announce("Paso 2: Configura el modo de combate")
    config.combat_mode = M.prompt_combat_mode()
    if not config.combat_mode then
        return nil
    end

    -- Step 3: Travel Speed
    vipzhyla.announce("Paso 3: Configura la velocidad de viaje")
    config.travel_speed = M.prompt_travel_speed()
    if not config.travel_speed then
        return nil
    end

    -- Step 4: Expert Mode
    vipzhyla.announce("Paso 4: Modo experto")
    config.expert_mode = M.prompt_expert_mode()
    if not config.expert_mode then
        return nil
    end

    -- Step 5: Audio Options
    vipzhyla.announce("Paso 5: Opciones de audio")
    config.audio_options = M.prompt_audio_options()
    if not config.audio_options then
        return nil
    end

    -- Complete
    vipzhyla.announce("Configuración completada")
    return config
end

function M.save_character_config(class_name, config)
    [[
    Save character configuration for loading on restart.

    Args:
        class_name: Character class name
        config: Configuration table with settings
    ]]

    -- Configuration will be saved to JSON by Python integration
    if vipzhyla.save_character_config then
        vipzhyla.save_character_config(class_name, config)
    end
end

function M.load_character_config(class_name)
    [[
    Load saved character configuration.

    Args:
        class_name: Character class name

    Returns:
        Configuration table or nil if not found
    ]]

    if vipzhyla.load_character_config then
        return vipzhyla.load_character_config(class_name)
    end

    return nil
end

return M

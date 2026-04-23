--[[
Estado Module - Character and game state tracking

Manages:
- Character state (name, level, class, race, HP, MP)
- Room state (name, exits, description)
- Combat state (in_combat, current_enemy, enemies list)
- General game flags and conditions

Data flow:
- GMCP is primary source (Char.Status, Char.Vitals, Room.Info)
- Text patterns are fallback for non-GMCP servers
- Events are emitted on state changes (health alerts, etc.)

Ported from: Funciones.set + Combate.set state tracking
--]]

local M = {}

-- Character state
local CHARACTER = {
    name = "",
    level = 0,
    class = "",
    race = "",
    experience = 0,
    hp = 0,
    maxhp = 0,
    mp = 0,
    maxmp = 0,
    energy = 0,
    maxenergy = 100,
}

-- Room state
local ROOM = {
    name = "Unknown",
    exits = {},
    description = "",
}

-- Combat state
local COMBAT = {
    in_combat = false,
    current_enemy = "",
    enemies = {},  -- List of current enemies
    last_attack_time = 0,
    health_critical_threshold = 30,  -- Announce at 30% HP
}

-- General flags
local FLAGS = {
    connected = false,
    logged_in = false,
    last_hp = 0,
    health_alerted = false,
}

-- Initialize module
function M.init(game)
    vipzhyla.say("[ESTADO] Initializing state tracking system")
end

-- ===== Character State Updates =====

function M.on_gmcp(module_name, data)
    if module_name == "Char.Status" then
        M.update_character_status(data)
    elseif module_name == "Char.Vitals" then
        M.update_vitals(data)
    elseif module_name == "Room.Info" then
        M.update_room(data)
    elseif module_name == "Room.Actual" then
        M.update_room_actual(data)
    end
end

function M.update_character_status(data)
    CHARACTER.name = data.name or ""
    CHARACTER.level = data.level or 0
    CHARACTER.class = data.class or ""
    CHARACTER.race = data.race or ""
    CHARACTER.experience = data.experience or 0

    if CHARACTER.name ~= "" then
        FLAGS.connected = true
        FLAGS.logged_in = true
    end
end

function M.update_vitals(data)
    local old_hp = CHARACTER.hp

    CHARACTER.hp = data.hp or 0
    CHARACTER.maxhp = data.maxhp or 0
    CHARACTER.mp = data.mp or 0
    CHARACTER.maxmp = data.maxmp or 0
    CHARACTER.energy = data.energy or CHARACTER.energy

    -- Check for health threshold
    if CHARACTER.hp > 0 and CHARACTER.maxhp > 0 then
        local health_percent = (CHARACTER.hp / CHARACTER.maxhp) * 100

        -- Alert if health drops below critical threshold
        if health_percent < COMBAT.health_critical_threshold and not COMBAT.health_alerted then
            vipzhyla.announce("¡ALERTA! Vida crítica: " .. CHARACTER.hp .. " de " .. CHARACTER.maxhp)
            COMBAT.health_alerted = true
        elseif health_percent > COMBAT.health_critical_threshold then
            COMBAT.health_alerted = false
        end

        -- Announce if HP changed significantly
        if old_hp > 0 and CHARACTER.hp ~= old_hp then
            local diff = CHARACTER.hp - old_hp
            if math.abs(diff) > 5 then  -- Only announce significant changes
                local direction = diff > 0 and "+" or ""
                vipzhyla.say("[VIDA] " .. direction .. diff .. " HP (" .. CHARACTER.hp .. "/" .. CHARACTER.maxhp .. ")")
            end
        end
    end

    FLAGS.last_hp = old_hp
end

function M.update_room(data)
    ROOM.name = data.name or "Unknown"
    ROOM.exits = data.exits or {}
    ROOM.description = data.desc or ""

    -- Announce room entry
    vipzhyla.say("[SALA] " .. ROOM.name)
    if #ROOM.exits > 0 then
        vipzhyla.say("[SALIDAS] " .. table.concat(ROOM.exits, ", "))
    end
end

function M.update_room_actual(data)
    ROOM.name = data or ROOM.name
end

-- ===== Combat State =====

function M.enter_combat(enemy)
    if not COMBAT.in_combat then
        COMBAT.in_combat = true
        COMBAT.current_enemy = enemy
        COMBAT.last_attack_time = os.time()
        vipzhyla.announce("¡Combate iniciado con " .. enemy .. "!")
    end
end

function M.exit_combat()
    if COMBAT.in_combat then
        COMBAT.in_combat = false
        COMBAT.current_enemy = ""
        COMBAT.enemies = {}
        vipzhyla.announce("Combate finalizado")
    end
end

function M.add_enemy(enemy_name)
    local exists = false
    for _, e in ipairs(COMBAT.enemies) do
        if e == enemy_name then
            exists = true
            break
        end
    end
    if not exists then
        table.insert(COMBAT.enemies, enemy_name)
    end
end

function M.remove_enemy(enemy_name)
    for i, e in ipairs(COMBAT.enemies) do
        if e == enemy_name then
            table.remove(COMBAT.enemies, i)
            break
        end
    end
end

function M.get_enemies()
    return COMBAT.enemies
end

-- ===== State Getters =====

function M.get_character()
    return CHARACTER
end

function M.get_character_name()
    return CHARACTER.name
end

function M.get_level()
    return CHARACTER.level
end

function M.get_class()
    return CHARACTER.class
end

function M.get_hp()
    return CHARACTER.hp
end

function M.get_maxhp()
    return CHARACTER.maxhp
end

function M.get_mp()
    return CHARACTER.mp
end

function M.get_maxmp()
    return CHARACTER.maxmp
end

function M.get_health_percent()
    if CHARACTER.maxhp == 0 then
        return 0
    end
    return (CHARACTER.hp / CHARACTER.maxhp) * 100
end

function M.get_room()
    return ROOM
end

function M.get_room_name()
    return ROOM.name
end

function M.get_exits()
    return ROOM.exits
end

function M.is_in_combat()
    return COMBAT.in_combat
end

function M.get_current_enemy()
    return COMBAT.current_enemy
end

-- ===== Status Display =====

function M.get_status()
    local status = CHARACTER.name .. " - Lvl " .. CHARACTER.level .. " " .. CHARACTER.class
    if CHARACTER.hp > 0 then
        status = status .. " - HP: " .. CHARACTER.hp .. "/" .. CHARACTER.maxhp
    end
    if COMBAT.in_combat then
        status = status .. " [EN COMBATE]"
    end
    return status
end

function M.log_status()
    vipzhyla.say("[PERSONAJE]")
    vipzhyla.say("  Nombre: " .. CHARACTER.name)
    vipzhyla.say("  Nivel: " .. CHARACTER.level)
    vipzhyla.say("  Clase: " .. CHARACTER.class)
    vipzhyla.say("  Raza: " .. CHARACTER.race)
    vipzhyla.say("[VITAL]")
    vipzhyla.say("  Vida: " .. CHARACTER.hp .. "/" .. CHARACTER.maxhp)
    vipzhyla.say("  Magia: " .. CHARACTER.mp .. "/" .. CHARACTER.maxmp)
    vipzhyla.say("[UBICACION]")
    vipzhyla.say("  Sala: " .. ROOM.name)
    if #ROOM.exits > 0 then
        vipzhyla.say("  Salidas: " .. table.concat(ROOM.exits, ", "))
    end
    if COMBAT.in_combat then
        vipzhyla.say("[COMBATE]")
        vipzhyla.say("  Enemigo: " .. COMBAT.current_enemy)
    end
end

-- ===== Flag Management =====

function M.is_connected()
    return FLAGS.connected
end

function M.set_connected(connected)
    FLAGS.connected = connected
    local status = connected and "Conectado" or "Desconectado"
    vipzhyla.announce("Estado: " .. status)
end

function M.is_logged_in()
    return FLAGS.logged_in
end

function M.set_logged_in(logged_in)
    FLAGS.logged_in = logged_in
end

return M

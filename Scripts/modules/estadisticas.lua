--[[
Estadísticas/Statistics System - Character and gameplay statistics

Tracks player statistics, achievements, and performance metrics.
Provides statistics collection, calculation, and reporting.

Phase 7A: Complete game state management
]]

local M = {}

-- Character statistics categories
local STAT_CATEGORIES = {
    combat = "Combat",
    economy = "Economy",
    social = "Social",
    progression = "Progression",
    gameplay = "Gameplay",
}

-- Character statistics structure
local character_stats = {
    -- Combat statistics
    combat = {
        total_kills = 0,
        total_deaths = 0,
        kills_by_type = {},      -- enemy_type -> count
        current_kill_streak = 0,
        max_kill_streak = 0,
        total_damage_dealt = 0,
        total_damage_taken = 0,
        total_heals = 0,
        critical_hits = 0,
        critical_rate = 0,        -- calculated
    },

    -- Economy statistics
    economy = {
        total_gold_earned = 0,
        total_gold_spent = 0,
        total_items_found = 0,
        total_items_sold = 0,
        total_items_bought = 0,
        richest_inventory = 0,    -- max gold held at once
        current_balance = 0,
    },

    -- Social statistics
    social = {
        quests_completed = 0,
        quests_failed = 0,
        quests_active = 0,
        npcs_met = 0,
        friends_count = 0,
        enemies_count = 0,
    },

    -- Progression statistics
    progression = {
        level = 0,
        experience = 0,
        experience_for_next = 0,
        levels_gained = 0,
        skills_learned = 0,
        spells_learned = 0,
        playtime_seconds = 0,
    },

    -- Gameplay statistics
    gameplay = {
        sessions_played = 0,
        total_playtime = 0,       -- in hours
        longest_session = 0,
        commands_executed = 0,
        rest_periods = 0,
        resurrection_count = 0,
    },
}

-- Session tracking
local current_session = {
    start_time = os.time(),
    kills = 0,
    deaths = 0,
    gold_gained = 0,
    commands = 0,
}

function M.init(game)
    game.estadisticas = game.estadisticas or {}
    game.estadisticas.stats = character_stats
    game.estadisticas.session = current_session
end

--[[ ===== Combat Statistics ===== ]]

function M.record_kill(enemy_type, damage_dealt)
    --[[Record a kill.]]
    character_stats.combat.total_kills = character_stats.combat.total_kills + 1
    character_stats.combat.current_kill_streak = character_stats.combat.current_kill_streak + 1

    -- Track max streak
    if character_stats.combat.current_kill_streak > character_stats.combat.max_kill_streak then
        character_stats.combat.max_kill_streak = character_stats.combat.current_kill_streak
    end

    -- Track by enemy type
    if not character_stats.combat.kills_by_type[enemy_type] then
        character_stats.combat.kills_by_type[enemy_type] = 0
    end
    character_stats.combat.kills_by_type[enemy_type] = character_stats.combat.kills_by_type[enemy_type] + 1

    if damage_dealt then
        character_stats.combat.total_damage_dealt = character_stats.combat.total_damage_dealt + damage_dealt
    end

    current_session.kills = current_session.kills + 1
end

function M.record_death(damage_taken)
    --[[Record a death.]]
    character_stats.combat.total_deaths = character_stats.combat.total_deaths + 1
    character_stats.combat.current_kill_streak = 0

    if damage_taken then
        character_stats.combat.total_damage_taken = character_stats.combat.total_damage_taken + damage_taken
    end

    current_session.deaths = current_session.deaths + 1
end

function M.record_damage_dealt(damage)
    --[[Record damage dealt.]]
    character_stats.combat.total_damage_dealt = character_stats.combat.total_damage_dealt + damage
end

function M.record_damage_taken(damage)
    --[[Record damage taken.]]
    character_stats.combat.total_damage_taken = character_stats.combat.total_damage_taken + damage
end

function M.record_heal(amount)
    --[[Record healing.]]
    character_stats.combat.total_heals = character_stats.combat.total_heals + amount
end

function M.record_critical_hit()
    --[[Record critical hit.]]
    character_stats.combat.critical_hits = character_stats.combat.critical_hits + 1
end

function M.get_kill_death_ratio()
    --[[Calculate K/D ratio.]]
    if character_stats.combat.total_deaths == 0 then
        return character_stats.combat.total_kills
    end
    return character_stats.combat.total_kills / character_stats.combat.total_deaths
end

--[[ ===== Economy Statistics ===== ]]

function M.record_gold_earned(amount)
    --[[Record gold earned.]]
    character_stats.economy.total_gold_earned = character_stats.economy.total_gold_earned + amount
    character_stats.economy.current_balance = character_stats.economy.current_balance + amount

    if character_stats.economy.current_balance > character_stats.economy.richest_inventory then
        character_stats.economy.richest_inventory = character_stats.economy.current_balance
    end

    current_session.gold_gained = current_session.gold_gained + amount
end

function M.record_gold_spent(amount)
    --[[Record gold spent.]]
    character_stats.economy.total_gold_spent = character_stats.economy.total_gold_spent + amount
    character_stats.economy.current_balance = character_stats.economy.current_balance - amount
end

function M.record_item_found(item_type)
    --[[Record item found.]]
    character_stats.economy.total_items_found = character_stats.economy.total_items_found + 1
end

function M.record_item_sold(gold_amount)
    --[[Record item sold.]]
    character_stats.economy.total_items_sold = character_stats.economy.total_items_sold + 1
    M.record_gold_earned(gold_amount)
end

function M.record_item_bought(gold_amount)
    --[[Record item bought.]]
    character_stats.economy.total_items_bought = character_stats.economy.total_items_bought + 1
    M.record_gold_spent(gold_amount)
end

--[[ ===== Progression Statistics ===== ]]

function M.set_level(level)
    --[[Set current level.]]
    local previous_level = character_stats.progression.level
    character_stats.progression.level = level

    if level > previous_level then
        character_stats.progression.levels_gained = character_stats.progression.levels_gained + (level - previous_level)
    end
end

function M.set_experience(exp, exp_for_next)
    --[[Set current experience.]]
    character_stats.progression.experience = exp
    character_stats.progression.experience_for_next = exp_for_next or 0
end

function M.record_spell_learned()
    --[[Record spell learned.]]
    character_stats.progression.spells_learned = character_stats.progression.spells_learned + 1
end

function M.record_skill_learned()
    --[[Record skill learned.]]
    character_stats.progression.skills_learned = character_stats.progression.skills_learned + 1
end

--[[ ===== Social Statistics ===== ]]

function M.record_quest_completed()
    --[[Record quest completed.]]
    character_stats.social.quests_completed = character_stats.social.quests_completed + 1
    if character_stats.social.quests_active > 0 then
        character_stats.social.quests_active = character_stats.social.quests_active - 1
    end
end

function M.record_quest_failed()
    --[[Record quest failed.]]
    character_stats.social.quests_failed = character_stats.social.quests_failed + 1
    if character_stats.social.quests_active > 0 then
        character_stats.social.quests_active = character_stats.social.quests_active - 1
    end
end

function M.record_quest_accepted()
    --[[Record quest accepted.]]
    character_stats.social.quests_active = character_stats.social.quests_active + 1
end

function M.record_npc_met()
    --[[Record meeting NPC.]]
    character_stats.social.npcs_met = character_stats.social.npcs_met + 1
end

--[[ ===== Gameplay Statistics ===== ]]

function M.record_command()
    --[[Record command executed.]]
    character_stats.gameplay.commands_executed = character_stats.gameplay.commands_executed + 1
    current_session.commands = current_session.commands + 1
end

function M.record_resurrection()
    --[[Record resurrection.]]
    character_stats.gameplay.resurrection_count = character_stats.gameplay.resurrection_count + 1
end

function M.end_session()
    --[[End current session and save stats.]]
    local session_duration = os.time() - current_session.start_time
    local session_hours = session_duration / 3600

    character_stats.gameplay.sessions_played = character_stats.gameplay.sessions_played + 1
    character_stats.gameplay.total_playtime = character_stats.gameplay.total_playtime + session_hours

    if session_hours > character_stats.gameplay.longest_session then
        character_stats.gameplay.longest_session = session_hours
    end

    vipzhyla.announce("Sesion finalizada. Duracion: " .. math.floor(session_hours * 60) .. " minutos")

    -- Reset session
    current_session = {
        start_time = os.time(),
        kills = 0,
        deaths = 0,
        gold_gained = 0,
        commands = 0,
    }
end

--[[ ===== Statistics Queries ===== ]]

function M.get_combat_stats()
    --[[Get combat statistics.]]
    return {
        kills = character_stats.combat.total_kills,
        deaths = character_stats.combat.total_deaths,
        kd_ratio = M.get_kill_death_ratio(),
        max_kill_streak = character_stats.combat.max_kill_streak,
        damage_dealt = character_stats.combat.total_damage_dealt,
        damage_taken = character_stats.combat.total_damage_taken,
        total_heals = character_stats.combat.total_heals,
        critical_hits = character_stats.combat.critical_hits,
    }
end

function M.get_economy_stats()
    --[[Get economy statistics.]]
    return {
        gold_earned = character_stats.economy.total_gold_earned,
        gold_spent = character_stats.economy.total_gold_spent,
        current_balance = character_stats.economy.current_balance,
        items_found = character_stats.economy.total_items_found,
        items_sold = character_stats.economy.total_items_sold,
        items_bought = character_stats.economy.total_items_bought,
    }
end

function M.get_progression_stats()
    --[[Get progression statistics.]]
    return {
        level = character_stats.progression.level,
        experience = character_stats.progression.experience,
        levels_gained = character_stats.progression.levels_gained,
        skills_learned = character_stats.progression.skills_learned,
        spells_learned = character_stats.progression.spells_learned,
    }
end

function M.get_session_stats()
    --[[Get current session statistics.]]
    local elapsed = os.time() - current_session.start_time
    return {
        duration = elapsed,
        kills = current_session.kills,
        deaths = current_session.deaths,
        gold_gained = current_session.gold_gained,
        commands = current_session.commands,
    }
end

--[[ ===== Statistics Display ===== ]]

function M.format_combat_stats()
    --[[Get formatted combat statistics.]]
    local stats = M.get_combat_stats()
    local lines = {}

    table.insert(lines, "=== COMBATE ===")
    table.insert(lines, "Muertes enemigos: " .. stats.kills)
    table.insert(lines, "Muertes propias: " .. stats.deaths)
    table.insert(lines, "Relacion K/D: " .. string.format("%.2f", stats.kd_ratio))
    table.insert(lines, "Racha maxima: " .. stats.max_kill_streak)
    table.insert(lines, "Danio infligido: " .. stats.damage_dealt)
    table.insert(lines, "Danio recibido: " .. stats.damage_taken)
    table.insert(lines, "Curaciones: " .. stats.total_heals)

    return table.concat(lines, "\n")
end

function M.format_economy_stats()
    --[[Get formatted economy statistics.]]
    local stats = M.get_economy_stats()
    local lines = {}

    table.insert(lines, "=== ECONOMIA ===")
    table.insert(lines, "Oro ganado: " .. stats.gold_earned)
    table.insert(lines, "Oro gastado: " .. stats.gold_spent)
    table.insert(lines, "Balance actual: " .. stats.current_balance)
    table.insert(lines, "Items encontrados: " .. stats.items_found)
    table.insert(lines, "Items vendidos: " .. stats.items_sold)
    table.insert(lines, "Items comprados: " .. stats.items_bought)

    return table.concat(lines, "\n")
end

function M.format_full_stats()
    --[[Get formatted full statistics report.]]
    local lines = {}

    table.insert(lines, "=== ESTADISTICAS ===")
    table.insert(lines, "")
    table.insert(lines, M.format_combat_stats())
    table.insert(lines, "")
    table.insert(lines, M.format_economy_stats())

    return table.concat(lines, "\n")
end

--[[ ===== Testing/Reset ===== ]]

function M.reset_stats()
    --[[Reset all statistics (for testing).]]
    character_stats = {
        combat = {
            total_kills = 0,
            total_deaths = 0,
            kills_by_type = {},
            current_kill_streak = 0,
            max_kill_streak = 0,
            total_damage_dealt = 0,
            total_damage_taken = 0,
            total_heals = 0,
            critical_hits = 0,
            critical_rate = 0,
        },
        economy = {
            total_gold_earned = 0,
            total_gold_spent = 0,
            total_items_found = 0,
            total_items_sold = 0,
            total_items_bought = 0,
            richest_inventory = 0,
            current_balance = 0,
        },
        social = {
            quests_completed = 0,
            quests_failed = 0,
            quests_active = 0,
            npcs_met = 0,
            friends_count = 0,
            enemies_count = 0,
        },
        progression = {
            level = 0,
            experience = 0,
            experience_for_next = 0,
            levels_gained = 0,
            skills_learned = 0,
            spells_learned = 0,
            playtime_seconds = 0,
        },
        gameplay = {
            sessions_played = 0,
            total_playtime = 0,
            longest_session = 0,
            commands_executed = 0,
            rest_periods = 0,
            resurrection_count = 0,
        },
    }
    vipzhyla.announce("Estadisticas reiniciadas")
end

function M.get_all_stats()
    --[[Return raw statistics table.]]
    return character_stats
end

return M

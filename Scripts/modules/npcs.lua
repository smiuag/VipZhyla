--[[
NPCs/Non-Player Characters System - NPC tracking and interaction

Tracks NPCs, their locations, states, and interactions.
Provides NPC detection, dialogue tracking, and relationship management.

Phase 7A: Complete game state management
]]

local M = {}

-- NPC types
local NPC_TYPES = {
    merchant = "Merchant",
    quest_giver = "Quest Giver",
    trainer = "Trainer",
    guard = "Guard",
    commoner = "Commoner",
    hostile = "Hostile",
    friendly = "Friendly",
    neutral = "Neutral",
}

-- Relationship levels
local RELATIONSHIP_LEVELS = {
    hostile = -2,
    unfriendly = -1,
    neutral = 0,
    friendly = 1,
    ally = 2,
}

-- NPC database
local npcs = {}
local npc_id_counter = 0

-- Active NPC interactions
local current_interactions = {}

-- NPC detection patterns
local NPC_DETECTION_PATTERNS = {
    "ves a",
    "You see",
    "esta aqui",
    "is here",
    "ante ti",
    "before you",
}

function M.init(game)
    game.npcs = game.npcs or {}
    game.npcs.list = npcs
    game.npcs.types = NPC_TYPES
    game.npcs.relationships = RELATIONSHIP_LEVELS
end

--[[ ===== NPC Management ===== ]]

function M.create_npc(name, npc_type, location, level)
    --[[
    Create/register new NPC.

    Args:
        name: NPC name
        npc_type: Type (merchant, quest_giver, etc.)
        location: Room name/location
        level: NPC level (optional)

    Returns:
        NPC ID
    ]]

    npc_id_counter = npc_id_counter + 1

    local npc = {
        id = npc_id_counter,
        name = name,
        type = npc_type,
        location = location,
        level = level or 0,
        relationship = 0,           -- neutral
        last_seen = os.time(),
        first_seen = os.time(),
        interaction_count = 0,
        dialogue_log = {},
        quest_provider = false,
        merchant = false,
        trainer = false,
        custom_data = {},
    }

    npcs[npc_id_counter] = npc
    vipzhyla.announce("NPC registrado: " .. name)

    return npc_id_counter
end

function M.get_npc(npc_id)
    --[[Get NPC by ID.]]
    return npcs[npc_id]
end

function M.get_npc_by_name(name)
    --[[Get NPC by name (case insensitive).]]
    local lower_name = name:lower()
    for _, npc in pairs(npcs) do
        if npc.name:lower() == lower_name then
            return npc
        end
    end
    return nil
end

function M.get_npcs_at_location(location)
    --[[Get all NPCs at specific location.]]
    local at_location = {}
    for _, npc in pairs(npcs) do
        if npc.location == location then
            table.insert(at_location, npc)
        end
    end
    return at_location
end

function M.get_npcs_by_type(npc_type)
    --[[Get all NPCs of specific type.]]
    local by_type = {}
    for _, npc in pairs(npcs) do
        if npc.type == npc_type then
            table.insert(by_type, npc)
        end
    end
    return by_type
end

function M.count_npcs()
    --[[Count total NPCs known.]]
    return npc_id_counter
end

--[[ ===== Location Updates ===== ]]

function M.update_npc_location(npc_id, new_location)
    --[[Update NPC location.]]
    if npcs[npc_id] then
        npcs[npc_id].location = new_location
        npcs[npc_id].last_seen = os.time()
        return true
    end
    return false
end

function M.set_npc_seen(npc_id)
    --[[Mark NPC as seen now.]]
    if npcs[npc_id] then
        npcs[npc_id].last_seen = os.time()
        return true
    end
    return false
end

function M.get_npc_last_seen(npc_id)
    --[[Get timestamp when NPC was last seen.]]
    if npcs[npc_id] then
        return npcs[npc_id].last_seen
    end
    return nil
end

--[[ ===== Relationship Management ===== ]]

function M.set_npc_relationship(npc_id, level)
    --[[
    Set NPC relationship level.

    Levels: -2=hostile, -1=unfriendly, 0=neutral, 1=friendly, 2=ally
    ]]

    if npcs[npc_id] then
        npcs[npc_id].relationship = math.max(-2, math.min(2, level))
        return true
    end
    return false
end

function M.adjust_npc_relationship(npc_id, delta)
    --[[Adjust relationship by delta amount.]]
    if npcs[npc_id] then
        npcs[npc_id].relationship = math.max(-2, math.min(2, npcs[npc_id].relationship + delta))
        return true
    end
    return false
end

function M.get_npc_relationship(npc_id)
    --[[Get NPC relationship level.]]
    if npcs[npc_id] then
        return npcs[npc_id].relationship
    end
    return nil
end

--[[ ===== Dialogue Tracking ===== ]]

function M.log_dialogue(npc_id, player_text, npc_response)
    --[[Log dialogue exchange with NPC.]]
    if not npcs[npc_id] then
        return false
    end

    local npc = npcs[npc_id]
    npc.interaction_count = npc.interaction_count + 1

    table.insert(npc.dialogue_log, {
        timestamp = os.time(),
        player_said = player_text or "",
        npc_said = npc_response or "",
    })

    -- Keep last 50 dialogue lines
    if #npc.dialogue_log > 50 then
        table.remove(npc.dialogue_log, 1)
    end

    return true
end

function M.get_dialogue_log(npc_id)
    --[[Get dialogue history with NPC.]]
    if npcs[npc_id] then
        return npcs[npc_id].dialogue_log
    end
    return nil
end

function M.get_interaction_count(npc_id)
    --[[Get total interactions with NPC.]]
    if npcs[npc_id] then
        return npcs[npc_id].interaction_count
    end
    return nil
end

--[[ ===== NPC Properties ===== ]]

function M.set_npc_quest_provider(npc_id, is_provider)
    --[[Mark NPC as quest provider.]]
    if npcs[npc_id] then
        npcs[npc_id].quest_provider = is_provider
        return true
    end
    return false
end

function M.set_npc_merchant(npc_id, is_merchant)
    --[[Mark NPC as merchant.]]
    if npcs[npc_id] then
        npcs[npc_id].merchant = is_merchant
        return true
    end
    return false
end

function M.set_npc_trainer(npc_id, is_trainer)
    --[[Mark NPC as trainer.]]
    if npcs[npc_id] then
        npcs[npc_id].trainer = is_trainer
        return true
    end
    return false
end

function M.set_npc_level(npc_id, level)
    --[[Set NPC level.]]
    if npcs[npc_id] then
        npcs[npc_id].level = level
        return true
    end
    return false
end

function M.set_custom_data(npc_id, key, value)
    --[[Store custom data on NPC.]]
    if npcs[npc_id] then
        npcs[npc_id].custom_data[key] = value
        return true
    end
    return false
end

function M.get_custom_data(npc_id, key)
    --[[Retrieve custom data from NPC.]]
    if npcs[npc_id] then
        return npcs[npc_id].custom_data[key]
    end
    return nil
end

--[[ ===== NPC Information ===== ]]

function M.get_npc_info(npc_id)
    --[[Get complete NPC information.]]
    if not npcs[npc_id] then
        return nil
    end

    local npc = npcs[npc_id]
    return {
        id = npc.id,
        name = npc.name,
        type = npc.type,
        location = npc.location,
        level = npc.level,
        relationship = npc.relationship,
        last_seen = npc.last_seen,
        first_seen = npc.first_seen,
        interaction_count = npc.interaction_count,
        is_quest_provider = npc.quest_provider,
        is_merchant = npc.merchant,
        is_trainer = npc.trainer,
    }
end

function M.format_npc_info(npc_id)
    --[[Get formatted NPC information string.]]
    if not npcs[npc_id] then
        return "Unknown NPC"
    end

    local npc = npcs[npc_id]
    local lines = {}

    table.insert(lines, "=== " .. npc.name:upper() .. " ===")
    table.insert(lines, "Type: " .. npc.type)
    table.insert(lines, "Location: " .. npc.location)

    if npc.level > 0 then
        table.insert(lines, "Level: " .. npc.level)
    end

    local rel_name = "Neutral"
    if npc.relationship == -2 then
        rel_name = "Hostile"
    elseif npc.relationship == -1 then
        rel_name = "Unfriendly"
    elseif npc.relationship == 1 then
        rel_name = "Friendly"
    elseif npc.relationship == 2 then
        rel_name = "Ally"
    end
    table.insert(lines, "Relationship: " .. rel_name)

    table.insert(lines, "Interactions: " .. npc.interaction_count)

    if npc.quest_provider then
        table.insert(lines, "[Provides quests]")
    end
    if npc.merchant then
        table.insert(lines, "[Sells items]")
    end
    if npc.trainer then
        table.insert(lines, "[Teaches skills]")
    end

    return table.concat(lines, "\n")
end

--[[ ===== Pattern Detection ===== ]]

function M.detect_npc_in_text(text)
    --[[Check if text mentions an NPC being present.]]
    for _, pattern in ipairs(NPC_DETECTION_PATTERNS) do
        if string.find(text:lower(), pattern:lower(), 1, true) then
            return true
        end
    end
    return false
end

--[[ ===== Statistics ===== ]]

function M.get_npc_stats()
    --[[Get NPC statistics.]]
    local stats = {
        total = npc_id_counter,
        by_type = {},
        friendly_count = 0,
        hostile_count = 0,
        quest_providers = 0,
        merchants = 0,
        trainers = 0,
    }

    for _, npc in pairs(npcs) do
        if not stats.by_type[npc.type] then
            stats.by_type[npc.type] = 0
        end
        stats.by_type[npc.type] = stats.by_type[npc.type] + 1

        if npc.relationship >= 1 then
            stats.friendly_count = stats.friendly_count + 1
        elseif npc.relationship <= -1 then
            stats.hostile_count = stats.hostile_count + 1
        end

        if npc.quest_provider then
            stats.quest_providers = stats.quest_providers + 1
        end
        if npc.merchant then
            stats.merchants = stats.merchants + 1
        end
        if npc.trainer then
            stats.trainers = stats.trainers + 1
        end
    end

    return stats
end

function M.format_npc_summary()
    --[[Get formatted NPC summary.]]
    local stats = M.get_npc_stats()
    local lines = {}

    table.insert(lines, "=== NPCs ===")
    table.insert(lines, "Total conocidos: " .. stats.total)
    table.insert(lines, "Amigos: " .. stats.friendly_count)
    table.insert(lines, "Hostiles: " .. stats.hostile_count)
    table.insert(lines, "Mercaderes: " .. stats.merchants)
    table.insert(lines, "Entrenadores: " .. stats.trainers)
    table.insert(lines, "Proveedores de misiones: " .. stats.quest_providers)

    return table.concat(lines, "\n")
end

--[[ ===== Testing/Reset ===== ]]

function M.clear_npcs()
    --[[Clear all NPCs (for testing).]]
    npcs = {}
    npc_id_counter = 0
    vipzhyla.announce("NPCs borrados")
end

function M.get_all_npcs()
    --[[Return all NPCs.]]
    return npcs
end

return M

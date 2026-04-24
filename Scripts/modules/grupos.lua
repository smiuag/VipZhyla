--[[
Grupos/Groups System - Party and group management

Manages player groups, parties, and group communication.
Provides party formation, member tracking, and group coordination.

Phase 7A: Complete game state management
]]

local M = {}

-- Party roles
local PARTY_ROLES = {
    leader = "Leader",
    officer = "Officer",
    member = "Member",
}

-- Party settings
local PARTY_SETTINGS = {
    max_members = 8,
    experience_sharing = true,
    loot_sharing = true,
    pvp_enabled = false,
}

-- Current party state
local party = {
    id = nil,
    name = "",
    leader = "",
    created_at = 0,
    members = {},           -- player_name -> {name, role, level, class, hp, maxhp, online}
    chat_log = {},
    formation = "loose",    -- loose, tight, column, etc.
}

-- Group/guild tracking
local known_groups = {}
local group_id_counter = 0

-- Party invitation pending
local pending_invitations = {}

function M.init(game)
    game.grupos = game.grupos or {}
    game.grupos.party = party
    game.grupos.groups = known_groups
    game.grupos.settings = PARTY_SETTINGS
    game.grupos.roles = PARTY_ROLES
end

--[[ ===== Party Formation ===== ]]

function M.create_party(player_name)
    --[[Create a new party.]]
    party.id = os.time()
    party.name = player_name .. "'s Party"
    party.leader = player_name
    party.created_at = os.time()
    party.members[player_name] = {
        name = player_name,
        role = "leader",
        level = 0,
        class = "",
        hp = 0,
        maxhp = 0,
        online = true,
    }

    vipzhyla.announce("Grupo creado: " .. party.name)
    return party.id
end

function M.disband_party()
    --[[Disband current party.]]
    if not party.id then
        return false
    end

    vipzhyla.announce("Grupo disuelto")

    party = {
        id = nil,
        name = "",
        leader = "",
        created_at = 0,
        members = {},
        chat_log = {},
        formation = "loose",
    }

    return true
end

function M.is_in_party()
    --[[Check if player is in a party.]]
    return party.id ~= nil
end

function M.get_party_info()
    --[[Get current party information.]]
    return {
        id = party.id,
        name = party.name,
        leader = party.leader,
        member_count = M.count_party_members(),
        max_members = PARTY_SETTINGS.max_members,
        exp_sharing = PARTY_SETTINGS.experience_sharing,
        loot_sharing = PARTY_SETTINGS.loot_sharing,
    }
end

--[[ ===== Party Members ===== ]]

function M.add_party_member(player_name, level, class)
    --[[Add member to party.]]
    if not party.id then
        return false
    end

    if M.count_party_members() >= PARTY_SETTINGS.max_members then
        vipzhyla.announce("El grupo esta lleno")
        return false
    end

    if party.members[player_name] then
        vipzhyla.announce(player_name .. " ya esta en el grupo")
        return false
    end

    party.members[player_name] = {
        name = player_name,
        role = "member",
        level = level or 0,
        class = class or "",
        hp = 0,
        maxhp = 0,
        online = true,
    }

    M.log_chat(party.leader, player_name .. " se unio al grupo")
    vipzhyla.announce(player_name .. " se unio al grupo")

    return true
end

function M.remove_party_member(player_name)
    --[[Remove member from party.]]
    if not party.members[player_name] then
        return false
    end

    party.members[player_name] = nil
    M.log_chat(party.leader, player_name .. " abandono el grupo")
    vipzhyla.announce(player_name .. " abandono el grupo")

    return true
end

function M.get_party_member(player_name)
    --[[Get party member details.]]
    return party.members[player_name]
end

function M.get_party_members()
    --[[Get list of all party members.]]
    local members = {}
    for name, member in pairs(party.members) do
        table.insert(members, member)
    end
    return members
end

function M.count_party_members()
    --[[Count party members.]]
    local count = 0
    for _ in pairs(party.members) do
        count = count + 1
    end
    return count
end

--[[ ===== Member Roles ===== ]]

function M.set_member_role(player_name, role)
    --[[Set player role in party.]]
    if not party.members[player_name] then
        return false
    end

    if not PARTY_ROLES[role] then
        return false
    end

    party.members[player_name].role = role
    vipzhyla.announce(player_name .. " es ahora " .. PARTY_ROLES[role])

    return true
end

function M.promote_to_leader(player_name)
    --[[Promote player to leader.]]
    if not party.members[player_name] then
        return false
    end

    -- Demote old leader
    if party.leader then
        party.members[party.leader].role = "officer"
    end

    -- Promote new leader
    party.leader = player_name
    party.members[player_name].role = "leader"
    vipzhyla.announce(player_name .. " es el nuevo lider del grupo")

    return true
end

--[[ ===== Party Communication ===== ]]

function M.log_chat(sender, message)
    --[[Log party chat message.]]
    local entry = {
        sender = sender,
        message = message,
        timestamp = os.time(),
    }

    table.insert(party.chat_log, entry)

    -- Keep last 100 messages
    if #party.chat_log > 100 then
        table.remove(party.chat_log, 1)
    end

    return true
end

function M.send_party_message(player_name, message)
    --[[Send message to party.]]
    if not party.id then
        vipzhyla.announce("No estás en un grupo")
        return false
    end

    M.log_chat(player_name, message)
    vipzhyla.announce("[GRUPO] " .. player_name .. ": " .. message)

    return true
end

function M.get_party_chat()
    --[[Get party chat history.]]
    return party.chat_log
end

function M.get_recent_party_messages(count)
    --[[Get last N party messages.]]
    local messages = {}
    local start = math.max(1, #party.chat_log - count + 1)

    for i = start, #party.chat_log do
        table.insert(messages, party.chat_log[i])
    end

    return messages
end

--[[ ===== Member Status ===== ]]

function M.update_member_status(player_name, hp, maxhp, online)
    --[[Update member HP and online status.]]
    if not party.members[player_name] then
        return false
    end

    party.members[player_name].hp = hp
    party.members[player_name].maxhp = maxhp
    party.members[player_name].online = online

    return true
end

function M.set_member_online(player_name, online)
    --[[Set member online status.]]
    if party.members[player_name] then
        party.members[player_name].online = online
        return true
    end
    return false
end

function M.get_online_members()
    --[[Get list of online party members.]]
    local online = {}
    for _, member in pairs(party.members) do
        if member.online then
            table.insert(online, member)
        end
    end
    return online
end

function M.count_online_members()
    --[[Count online party members.]]
    return #M.get_online_members()
end

--[[ ===== Party Settings ===== ]]

function M.set_experience_sharing(enabled)
    --[[Enable/disable experience sharing.]]
    PARTY_SETTINGS.experience_sharing = enabled
    vipzhyla.announce("Compartir experiencia: " .. (enabled and "Activado" or "Desactivado"))
    return true
end

function M.set_loot_sharing(enabled)
    --[[Enable/disable loot sharing.]]
    PARTY_SETTINGS.loot_sharing = enabled
    vipzhyla.announce("Compartir botin: " .. (enabled and "Activado" or "Desactivado"))
    return true
end

function M.set_party_formation(formation)
    --[[Set party formation.]]
    local valid_formations = {loose = true, tight = true, column = true, circle = true}

    if not valid_formations[formation] then
        return false
    end

    party.formation = formation
    vipzhyla.announce("Formacion: " .. formation)

    return true
end

function M.get_party_settings()
    --[[Get party settings.]]
    return {
        max_members = PARTY_SETTINGS.max_members,
        exp_sharing = PARTY_SETTINGS.experience_sharing,
        loot_sharing = PARTY_SETTINGS.loot_sharing,
        formation = party.formation,
    }
end

--[[ ===== Invitations ===== ]]

function M.invite_player(inviter, invitee)
    --[[Invite player to party.]]
    if not party.id then
        return false
    end

    pending_invitations[invitee] = {
        from = inviter,
        timestamp = os.time(),
        party_id = party.id,
    }

    vipzhyla.announce(invitee .. " ha sido invitado al grupo")
    return true
end

function M.accept_invitation(player_name)
    --[[Accept party invitation.]]
    if not pending_invitations[player_name] then
        return false
    end

    pending_invitations[player_name] = nil
    return M.add_party_member(player_name, 0, "")
end

function M.reject_invitation(player_name)
    --[[Reject party invitation.]]
    if not pending_invitations[player_name] then
        return false
    end

    pending_invitations[player_name] = nil
    vipzhyla.announce("Invitacion rechazada")
    return true
end

function M.get_pending_invitation(player_name)
    --[[Get pending invitation details.]]
    return pending_invitations[player_name]
end

--[[ ===== Party Information Display ===== ]]

function M.format_party_info()
    --[[Get formatted party information.]]
    if not party.id then
        return "No estas en un grupo"
    end

    local lines = {}
    table.insert(lines, "=== " .. party.name .. " ===")
    table.insert(lines, "Lider: " .. party.leader)
    table.insert(lines, "Miembros: " .. M.count_party_members() .. " / " .. PARTY_SETTINGS.max_members)
    table.insert(lines, "En linea: " .. M.count_online_members())
    table.insert(lines, "Compartir exp: " .. (PARTY_SETTINGS.experience_sharing and "Si" or "No"))
    table.insert(lines, "Compartir botin: " .. (PARTY_SETTINGS.loot_sharing and "Si" or "No"))
    table.insert(lines, "")
    table.insert(lines, "Miembros:")

    for _, member in pairs(party.members) do
        local status = member.online and "[EN LINEA]" or "[DESCONECTADO]"
        local hp_bar = ""
        if member.maxhp > 0 then
            hp_bar = " HP: " .. member.hp .. "/" .. member.maxhp
        end
        table.insert(lines, "  " .. member.name .. " (" .. member.role .. ") " .. status .. hp_bar)
    end

    return table.concat(lines, "\n")
end

--[[ ===== Testing/Reset ===== ]]

function M.clear_party()
    --[[Clear party (for testing).]]
    party = {
        id = nil,
        name = "",
        leader = "",
        created_at = 0,
        members = {},
        chat_log = {},
        formation = "loose",
    }
    pending_invitations = {}
    vipzhyla.announce("Grupo borrado")
end

function M.get_party_state()
    --[[Return raw party state.]]
    return party
end

return M

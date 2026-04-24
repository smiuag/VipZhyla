--[[
Inventario/Items System - Complete item management and equipment

Manages player inventory with weight limits, equipment slots, consumables,
and automatic detection of new items.

Phase 7A: Complete game state management
]]

local M = {}

-- Equipment slots
local EQUIPMENT_SLOTS = {
    head = {slot = "head", name = "Cabeza"},
    body = {slot = "body", name = "Cuerpo"},
    hands = {slot = "hands", name = "Manos"},
    feet = {slot = "feet", name = "Pies"},
    back = {slot = "back", name = "Espalda"},
    hands_left = {slot = "hands_left", name = "Mano Izquierda"},
    hands_right = {slot = "hands_right", name = "Mano Derecha"},
    waist = {slot = "waist", name = "Cintura"},
    neck = {slot = "neck", name = "Cuello"},
    wrist_left = {slot = "wrist_left", name = "Muñeca Izquierda"},
    wrist_right = {slot = "wrist_right", name = "Muñeca Derecha"},
    ring_left = {slot = "ring_left", name = "Anillo Izquierdo"},
    ring_right = {slot = "ring_right", name = "Anillo Derecho"},
}

-- Item quality tiers
local ITEM_QUALITY = {
    common = {value = 1, name = "Común"},
    uncommon = {value = 2, name = "Poco Común"},
    rare = {value = 3, name = "Raro"},
    epic = {value = 4, name = "Épico"},
    legendary = {value = 5, name = "Legendario"},
}

-- Item types
local ITEM_TYPES = {
    weapon = "Arma",
    armor = "Armadura",
    potion = "Poción",
    scroll = "Pergamino",
    crafting = "Material de Artesanía",
    consumable = "Consumible",
    misc = "Miscelánea",
    quest = "Quest",
    valuables = "Valuables",
}

-- Player inventory state
local inventory = {
    items = {},        -- item_id -> {id, name, qty, weight, type, quality}
    equipped = {},     -- slot -> item_id
    total_weight = 0,
    max_weight = 100,  -- Default, can be upgraded
}

-- Item database (for lookups)
local item_database = {}

-- Detection patterns for item gains/losses
local ITEM_GAIN_PATTERNS = {
    "Obtienes",
    "recibes",
    "ganaste",
    "obtienen",
    "recebes",
}

local ITEM_LOSS_PATTERNS = {
    "pierdes",
    "perdiste",
    "desaparece",
    "se desvanece",
    "cae al suelo",
}

function M.init(game)
    game.inventario = game.inventario or {}
    game.inventario.inventory = inventory
    game.inventario.database = item_database
end

--[[ ===== Item Management ===== ]]

function M.add_item(item_id, name, quantity, weight, item_type, quality)
    --[[
    Add item to inventory.

    Args:
        item_id: Unique identifier
        name: Item name
        quantity: How many (for stackables)
        weight: Weight per unit
        item_type: Type (weapon, armor, potion, etc.)
        quality: Quality tier (common, rare, epic, etc.)

    Returns:
        true if added successfully
    ]]

    -- Check weight limit
    local total_new_weight = inventory.total_weight + (weight * quantity)
    if total_new_weight > inventory.max_weight then
        vipzhyla.announce("No tienes espacio en tu inventario")
        return false
    end

    -- Add or update item
    if inventory.items[item_id] then
        -- Already have this item, increment quantity
        inventory.items[item_id].qty = inventory.items[item_id].qty + quantity
    else
        -- New item
        inventory.items[item_id] = {
            id = item_id,
            name = name,
            qty = quantity,
            weight = weight,
            type = item_type or "misc",
            quality = quality or "common",
            acquired_time = os.time(),
        }
    end

    inventory.total_weight = total_new_weight
    vipzhyla.announce("Obtienes: " .. name .. " x" .. quantity)

    return true
end

function M.remove_item(item_id, quantity)
    --[[
    Remove item from inventory.

    Args:
        item_id: Item identifier
        quantity: How many to remove (nil = remove all)

    Returns:
        true if removed successfully
    ]]

    if not inventory.items[item_id] then
        return false
    end

    local item = inventory.items[item_id]
    local remove_qty = quantity or item.qty

    if remove_qty >= item.qty then
        -- Remove all
        inventory.total_weight = inventory.total_weight - (item.weight * item.qty)
        local name = item.name
        inventory.items[item_id] = nil
        vipzhyla.announce("Pierdes: " .. name)
        return true
    else
        -- Partial removal
        item.qty = item.qty - remove_qty
        inventory.total_weight = inventory.total_weight - (item.weight * remove_qty)
        return true
    end
end

function M.has_item(item_id)
    --[[Check if item is in inventory.]]
    return inventory.items[item_id] ~= nil
end

function M.get_item(item_id)
    --[[Get item details.]]
    return inventory.items[item_id]
end

function M.get_item_count(item_id)
    --[[Get quantity of specific item.]]
    local item = inventory.items[item_id]
    return item and item.qty or 0
end

--[[ ===== Equipment Management ===== ]]

function M.equip_item(item_id, slot)
    --[[
    Equip item to specific slot.

    Args:
        item_id: Item to equip
        slot: Equipment slot (head, body, hands, etc.)

    Returns:
        true if equipped successfully
    ]]

    if not M.has_item(item_id) then
        return false
    end

    if not EQUIPMENT_SLOTS[slot] then
        return false
    end

    -- Unequip previous item in that slot
    if inventory.equipped[slot] then
        M.unequip_item(slot)
    end

    inventory.equipped[slot] = item_id
    local item = inventory.items[item_id]
    vipzhyla.announce("Equippado: " .. item.name .. " (" .. EQUIPMENT_SLOTS[slot].name .. ")")

    return true
end

function M.unequip_item(slot)
    --[[
    Unequip item from slot.

    Args:
        slot: Equipment slot

    Returns:
        true if unequipped successfully
    ]]

    if not inventory.equipped[slot] then
        return false
    end

    local item_id = inventory.equipped[slot]
    local item = inventory.items[item_id]
    inventory.equipped[slot] = nil

    vipzhyla.announce("Desiquippado: " .. item.name)
    return true
end

function M.get_equipped_item(slot)
    --[[Get equipped item in slot.]]
    return inventory.equipped[slot]
end

function M.is_equipped(item_id)
    --[[Check if item is equipped.]]
    for _, equipped_id in pairs(inventory.equipped) do
        if equipped_id == item_id then
            return true
        end
    end
    return false
end

function M.get_all_equipped()
    --[[Return table of all equipped items.]]
    return inventory.equipped
end

--[[ ===== Inventory Queries ===== ]]

function M.get_inventory()
    --[[Return current inventory state.]]
    return inventory.items
end

function M.get_weight_status()
    --[[Get weight usage information.]]
    return {
        current = inventory.total_weight,
        max = inventory.max_weight,
        percent = (inventory.total_weight / inventory.max_weight) * 100,
    }
end

function M.is_inventory_full()
    --[[Check if inventory at weight limit.]]
    return inventory.total_weight >= inventory.max_weight
end

function M.get_free_weight()
    --[[Get available weight remaining.]]
    return inventory.max_weight - inventory.total_weight
end

function M.get_items_by_type(item_type)
    --[[Get all items of specific type.]]
    local items = {}
    for id, item in pairs(inventory.items) do
        if item.type == item_type then
            table.insert(items, item)
        end
    end
    return items
end

function M.get_consumables()
    --[[Get all consumable items (potions, scrolls).]]
    return M.get_items_by_type("potion") or {}
end

function M.count_items()
    --[[Count total number of item stacks.]]
    local count = 0
    for _ in pairs(inventory.items) do
        count = count + 1
    end
    return count
end

function M.count_weight_usage()
    --[[Count weight used by different types.]]
    local by_type = {}
    for _, item in pairs(inventory.items) do
        if not by_type[item.type] then
            by_type[item.type] = 0
        end
        by_type[item.type] = by_type[item.type] + (item.weight * item.qty)
    end
    return by_type
end

--[[ ===== Weight Management ===== ]]

function M.increase_max_weight(amount)
    --[[Increase carrying capacity (from leveling/buffs).]]
    inventory.max_weight = inventory.max_weight + amount
    vipzhyla.announce("Capacidad de carga aumentada: " .. inventory.max_weight)
end

--[[ ===== Pattern Detection ===== ]]

function M.detect_item_gain(text)
    --[[
    Detect item gain from MUD message.

    Returns:
        Item name if detected, nil otherwise
    ]]

    for _, pattern in ipairs(ITEM_GAIN_PATTERNS) do
        if string.find(text:lower(), pattern:lower(), 1, true) then
            -- Try to extract item name
            -- This is simplified - real parsing would extract the item name
            return "unknown_item"
        end
    end
    return nil
end

function M.detect_item_loss(text)
    --[[
    Detect item loss from MUD message.

    Returns:
        true if loss detected
    ]]

    for _, pattern in ipairs(ITEM_LOSS_PATTERNS) do
        if string.find(text:lower(), pattern:lower(), 1, true) then
            return true
        end
    end
    return false
end

--[[ ===== Consumable Usage ===== ]]

function M.use_item(item_id)
    --[[
    Use a consumable item (potion, scroll, etc.).

    Args:
        item_id: Item to consume

    Returns:
        true if consumed successfully
    ]]

    local item = M.get_item(item_id)
    if not item then
        return false
    end

    if item.type ~= "potion" and item.type ~= "consumable" then
        vipzhyla.announce("No puedes usar este item")
        return false
    end

    vipzhyla.announce("Usas: " .. item.name)
    return M.remove_item(item_id, 1)
end

--[[ ===== Inventory Display ===== ]]

function M.format_inventory()
    --[[Return formatted inventory string for display.]]
    local lines = {}
    table.insert(lines, "=== INVENTARIO ===")

    for id, item in pairs(inventory.items) do
        local equipped_marker = M.is_equipped(id) and "[E] " or "    "
        local line = string.format(
            "%s%s x%d (%.1f kg)",
            equipped_marker,
            item.name,
            item.qty,
            item.weight * item.qty
        )
        table.insert(lines, line)
    end

    local weight_status = M.get_weight_status()
    table.insert(lines, "")
    table.insert(lines, string.format(
        "Peso: %.1f / %.1f kg (%.0f%%)",
        weight_status.current,
        weight_status.max,
        weight_status.percent
    ))

    return table.concat(lines, "\n")
end

--[[ ===== Testing/Reset ===== ]]

function M.clear_inventory()
    --[[Clear all items (for testing).]]
    inventory.items = {}
    inventory.equipped = {}
    inventory.total_weight = 0
    vipzhyla.announce("Inventario vaciado")
end

function M.get_inventory_state()
    --[[Return raw inventory state.]]
    return {
        items = inventory.items,
        equipped = inventory.equipped,
        total_weight = inventory.total_weight,
        max_weight = inventory.max_weight,
    }
end

return M

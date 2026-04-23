--[[
VipZhyla Lua Helper Functions

Provides utility functions for string manipulation, list operations,
and other common tasks (ported from MushClient functions).
--]]

local M = {}

-- String manipulation (ported from MushClient)

function M.trim(str)
    return str:match("^%s*(.-)%s*$")
end

function M.ltrim(str)
    return str:match("^%s*(.*)")
end

function M.rtrim(str)
    return str:match("(.-)%s*$")
end

function M.split(str, delimiter)
    local result = {}
    local pattern = "([^" .. delimiter .. "]+)"
    for match in str:gmatch(pattern) do
        table.insert(result, match)
    end
    return result
end

function M.join(list, delimiter)
    return table.concat(list, delimiter)
end

function M.replace(str, old, new)
    return str:gsub(old:gsub("%%", "%%%%"), new:gsub("%%", "%%%%"), 1)
end

function M.replace_all(str, old, new)
    return str:gsub(old:gsub("%%", "%%%%"), new:gsub("%%", "%%%%"))
end

function M.starts_with(str, prefix)
    return str:sub(1, #prefix) == prefix
end

function M.ends_with(str, suffix)
    return str:sub(-#suffix) == suffix
end

function M.contains(str, substring)
    return str:find(substring, 1, true) ~= nil
end

function M.upper(str)
    return str:upper()
end

function M.lower(str)
    return str:lower()
end

function M.length(str)
    return #str
end

-- List operations (ported from MushClient)

function M.list_count(list, delimiter)
    if not list or list == "" then
        return 0
    end
    local parts = M.split(list, delimiter)
    return #parts
end

function M.list_item(list, index, delimiter)
    local parts = M.split(list, delimiter)
    return parts[index]
end

function M.list_find(list, value, delimiter)
    local parts = M.split(list, delimiter)
    for i, v in ipairs(parts) do
        if v == value then
            return i
        end
    end
    return 0
end

function M.list_add(list, value, delimiter)
    if not list or list == "" then
        return value
    end
    return list .. delimiter .. value
end

function M.list_remove(list, index, delimiter)
    local parts = M.split(list, delimiter)
    table.remove(parts, index)
    return M.join(parts, delimiter)
end

-- Math operations

function M.abs(n)
    return math.abs(n)
end

function M.min(a, b)
    return math.min(a, b)
end

function M.max(a, b)
    return math.max(a, b)
end

function M.clamp(value, min_val, max_val)
    return math.max(min_val, math.min(value, max_val))
end

-- Conversions

function M.to_number(str)
    return tonumber(str) or 0
end

function M.to_string(val)
    return tostring(val)
end

-- Logging (will be exposed from Python)

function M.log(message)
    vipzhyla.say("[LOG] " .. tostring(message))
end

function M.debug(message)
    vipzhyla.say("[DEBUG] " .. tostring(message))
end

function M.error(message)
    vipzhyla.say("[ERROR] " .. tostring(message))
end

return M

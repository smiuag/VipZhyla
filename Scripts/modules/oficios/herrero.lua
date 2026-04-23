local M = {}

local patterns = {
  start = "Comienzas a forjar",
  turn = {
    "golpeas el metal",
    "Aprietas los dientes",
    "Calientas el metal",
    "Trabajas con cuidado",
  },
  success = "Forjas",
  fuel_depleted = "falta de combustible",
  melted = "se funde",
  stop = "Detienes el proceso de forjado",
  hammer_break = "martillo se rompe",
  metal_cracked = "el metal se agrieta",
}

function M.init(game)
  game.oficios = game.oficios or {}
  game.oficios.herrero = {
    patterns = patterns,
    active = false,
  }
end

function M.detect_start(text)
  return string.find(text, patterns.start, 1, true) and "start" or nil
end

function M.detect_turn(text)
  for _, pattern in ipairs(patterns.turn) do
    if string.find(text, pattern, 1, true) then
      return "turn"
    end
  end
  return nil
end

function M.detect_success(text)
  return string.find(text, patterns.success, 1, true) and "success" or nil
end

function M.detect_failure(text)
  if string.find(text, patterns.fuel_depleted, 1, true) then
    return "fuel_depleted"
  end
  if string.find(text, patterns.melted, 1, true) then
    return "melted"
  end
  if string.find(text, patterns.hammer_break, 1, true) then
    return "hammer_break"
  end
  if string.find(text, patterns.metal_cracked, 1, true) then
    return "metal_cracked"
  end
  return nil
end

function M.detect_stop(text)
  return string.find(text, patterns.stop, 1, true) and "stop" or nil
end

function M.detect_event(text)
  if string.find(text, patterns.hammer_break, 1, true) then
    return "tool_damage"
  end
  if string.find(text, patterns.metal_cracked, 1, true) then
    return "material_damage"
  end
  return nil
end

function M.get_patterns()
  return patterns
end

return M

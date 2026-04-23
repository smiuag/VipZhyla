local M = {}

local patterns = {
  start = "Comienzas la extracci%an del mineral",
  turn = {
    "Picas fervientemente sobre",
    "Con un peque%ao grito descargas",
    "Gotas de sudor corren por tu cara",
    "Golpeas la"
  },
  success = "Consigues extraer",
  exhausted_vein = "esta veta est%a agotada",
  confused = "No has logrado encontrar mineral",
  stop = "Detienes la extracci%an del mineral",
  flood = "Se abierto una brecha que comunica con un r%ao subterr%aneo",
  collapse = "Los soportes de la mina crujen y se produce un desprendimiento",
  blocked = "Las rocas tapan la salida",
  explosion = "Se ha producido una explosi%an de gas",
}

function M.init(game)
  game.oficios = game.oficios or {}
  game.oficios.minero = {
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
  if string.find(text, patterns.exhausted_vein, 1, true) then
    return "exhausted_vein"
  end
  if string.find(text, patterns.confused, 1, true) then
    return "confused"
  end
  return nil
end

function M.detect_stop(text)
  return string.find(text, patterns.stop, 1, true) and "stop" or nil
end

function M.detect_event(text)
  if string.find(text, patterns.flood, 1, true) then
    return "flood"
  end
  if string.find(text, patterns.collapse, 1, true) then
    return "collapse"
  end
  if string.find(text, patterns.blocked, 1, true) then
    return "blocked"
  end
  if string.find(text, patterns.explosion, 1, true) then
    return "explosion"
  end
  return nil
end

function M.get_patterns()
  return patterns
end

return M

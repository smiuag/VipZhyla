local M = {}

local patterns = {
  start = {
    "Comienzas a trabajar",
    "Aceptas un trabajo",
  },
  turn = {
    "Trabajas duro",
    "Sigues trabajando",
    "Sudas mientras trabajas",
    "Realizas tu tarea",
  },
  success = {
    "Has completado tu tarea",
    "El trabajo est%a terminado",
    "Consigues tu paga",
  },
  exhausted = "demasiado cansado",
  failed = "No consigues terminar",
  accident = "se produce un accidente",
  stop = {
    "Detienes tu trabajo",
    "Abandonas tu trabajo",
  },
  injury = "Te lesionas",
  tool_break = "tu herramienta se rompe",
}

function M.init(game)
  game.oficios = game.oficios or {}
  game.oficios.jornalero = {
    patterns = patterns,
    active = false,
  }
end

function M.detect_start(text)
  for _, pattern in ipairs(patterns.start) do
    if string.find(text, pattern, 1, true) then
      return "start"
    end
  end
  return nil
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
  for _, pattern in ipairs(patterns.success) do
    if string.find(text, pattern, 1, true) then
      return "success"
    end
  end
  return nil
end

function M.detect_failure(text)
  if string.find(text, patterns.exhausted, 1, true) then
    return "exhausted"
  end
  if string.find(text, patterns.failed, 1, true) then
    return "failed"
  end
  if string.find(text, patterns.accident, 1, true) then
    return "accident"
  end
  return nil
end

function M.detect_stop(text)
  for _, pattern in ipairs(patterns.stop) do
    if string.find(text, pattern, 1, true) then
      return "stop"
    end
  end
  return nil
end

function M.detect_event(text)
  if string.find(text, patterns.injury, 1, true) then
    return "injury"
  end
  if string.find(text, patterns.tool_break, 1, true) then
    return "tool_break"
  end
  if string.find(text, patterns.accident, 1, true) then
    return "accident"
  end
  return nil
end

function M.get_patterns()
  return patterns
end

return M

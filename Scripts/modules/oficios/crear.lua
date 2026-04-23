local M = {}

local patterns = {
  start = {
    "Comienzas a crear",
    "Inicias la creaci%an",
    "Comienzas el proceso",
  },
  turn = {
    "Trabajas en tu creaci%an",
    "Refinas tu trabajo",
    "Sigues creando",
    "Haces progreso",
  },
  component = {
    "A%aades un componente",
    "Incorporas",
    "Integras",
  },
  success = {
    "Has creado",
    "Tu creaci%an est%a lista",
    "Completaste tu creaci%an",
  },
  failed = {
    "Tu creaci%an se ha arruinado",
    "No consigues crear",
  },
  insufficient = "No tienes suficientes",
  quality_degrades = "La calidad se degrada",
  stop = {
    "Detienes la creaci%an",
    "Abandonas tu creaci%an",
  },
  material_breaks = "el material se rompe",
  component_lost = "Un componente se pierde",
}

function M.init(game)
  game.oficios = game.oficios or {}
  game.oficios.crear = {
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

function M.detect_component(text)
  for _, pattern in ipairs(patterns.component) do
    if string.find(text, pattern, 1, true) then
      return "component"
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
  for _, pattern in ipairs(patterns.failed) do
    if string.find(text, pattern, 1, true) then
      return "failed"
    end
  end
  if string.find(text, patterns.insufficient, 1, true) then
    return "insufficient_materials"
  end
  if string.find(text, patterns.quality_degrades, 1, true) then
    return "quality_degraded"
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
  if string.find(text, patterns.material_breaks, 1, true) then
    return "material_break"
  end
  if string.find(text, patterns.component_lost, 1, true) then
    return "component_lost"
  end
  return nil
end

function M.get_patterns()
  return patterns
end

return M

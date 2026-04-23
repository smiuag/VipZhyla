local M = {}

local patterns = {
  start = "Comienzas a pescar",
  cast = {
    "Lanzas tu ca%ana",
    "Recoges tu ca%ana",
    "Esperas pacientemente",
    "Mantienes el anzuelo",
  },
  bite = "pica el anzuelo",
  success = "Consigues capturar",
  too_tired = "demasiado cansado",
  no_fish = "No hay peces aqu%a",
  weather = "El clima es demasiado malo",
  stop = "Detienes la pesca",
  line_break = "Se rompe el sedal",
  hook_lost = "Pierdes el anzuelo",
  storm = "Se acerca una tormenta",
}

function M.init(game)
  game.oficios = game.oficios or {}
  game.oficios.marinero = {
    patterns = patterns,
    active = false,
  }
end

function M.detect_start(text)
  return string.find(text, patterns.start, 1, true) and "start" or nil
end

function M.detect_cast(text)
  for _, pattern in ipairs(patterns.cast) do
    if string.find(text, pattern, 1, true) then
      return "cast"
    end
  end
  return nil
end

function M.detect_bite(text)
  return string.find(text, patterns.bite, 1, true) and "bite" or nil
end

function M.detect_success(text)
  return string.find(text, patterns.success, 1, true) and "success" or nil
end

function M.detect_failure(text)
  if string.find(text, patterns.too_tired, 1, true) then
    return "too_tired"
  end
  if string.find(text, patterns.no_fish, 1, true) then
    return "no_fish"
  end
  if string.find(text, patterns.weather, 1, true) then
    return "bad_weather"
  end
  return nil
end

function M.detect_stop(text)
  return string.find(text, patterns.stop, 1, true) and "stop" or nil
end

function M.detect_event(text)
  if string.find(text, patterns.line_break, 1, true) then
    return "line_break"
  end
  if string.find(text, patterns.hook_lost, 1, true) then
    return "hook_lost"
  end
  if string.find(text, patterns.storm, 1, true) then
    return "storm"
  end
  return nil
end

function M.get_patterns()
  return patterns
end

return M

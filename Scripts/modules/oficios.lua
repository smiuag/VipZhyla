local M = {}

local function new_profession(name)
  local prof = {
    name = name,
    active = false,
    turn_count = 0,
    success_count = 0,
    failure_count = 0,
    last_action = nil,
    last_result = nil,
  }
  return prof
end

local professions = {
  minero = new_profession("Minero"),
  herrero = new_profession("Herrero"),
  marinero = new_profession("Marinero"),
  jornalero = new_profession("Jornalero"),
  crear = new_profession("Crear"),
}

function M.init(game)
  game.professions = professions
end

function M.get_active_profession()
  for name, prof in pairs(professions) do
    if prof.active then
      return name, prof
    end
  end
  return nil, nil
end

function M.start_profession(name)
  if professions[name] then
    M.stop_profession()
    professions[name].active = true
    professions[name].turn_count = 0
    professions[name].success_count = 0
    professions[name].failure_count = 0
    return true
  end
  return false
end

function M.stop_profession()
  for name, prof in pairs(professions) do
    prof.active = false
  end
end

function M.increment_turn(name)
  if professions[name] then
    professions[name].turn_count = professions[name].turn_count + 1
    return professions[name].turn_count
  end
  return nil
end

function M.register_success(name, action)
  if professions[name] then
    professions[name].success_count = professions[name].success_count + 1
    professions[name].last_action = action
    professions[name].last_result = "success"
  end
end

function M.register_failure(name, action, reason)
  if professions[name] then
    professions[name].failure_count = professions[name].failure_count + 1
    professions[name].last_action = action
    professions[name].last_result = reason or "failure"
  end
end

function M.get_profession(name)
  return professions[name]
end

function M.get_all_professions()
  return professions
end

function M.get_stats(name)
  if professions[name] then
    local prof = professions[name]
    return {
      turns = prof.turn_count,
      successes = prof.success_count,
      failures = prof.failure_count,
      last_action = prof.last_action,
      last_result = prof.last_result,
    }
  end
  return nil
end

return M

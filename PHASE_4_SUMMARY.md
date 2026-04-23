# Phase 4 Complete — Map/Navigation System

## Summary
Implemented automatic position tracking, room localization, and client-side navigation with pathfinding. Player position updates automatically via GMCP Room.Movimiento (whether moving manually or following another player). Includes manual locate command, search-and-navigate (irsala), and automatic walk execution.

## Changes

### New Files

**`src/models/map_service.py`** (340 lines)
- `MapRoom` dataclass: id, short name, coordinates, exits dict, full name
- `MapService` class:
  - `load(json_path)` → loads map-reinos.json (28816 rooms, 4073 name entries)
  - `find_room(line)` → parses "Name [exits]" format, resolves room with disambiguation
  - `set_current_room()` / `get_current_room()` → position tracking
  - `move_by_direction(direction)` → updates position via exit lookup
  - `search_rooms(query)` → substring search, max 20 results
  - `find_path(from_id, to_id)` → BFS pathfinding, max 50K nodes, returns list of MUD commands

**Direction Key Normalization:**
- Spanish MUD words ↔ short keys: norte↔n, sur↔s, este↔e, oeste↔o, noreste↔ne, noroeste↔no, sureste↔se, suroeste↔so, arriba↔ar, abajo↔ab, dentro↔de, fuera↔fu

**`src/data/map-reinos.json`**
- Copied from BlowTorch (`src/assets/map-reinos.json`)
- Same Reinos de Leyenda MUD, same rooms, no conversion needed
- Format: `{rooms: {id: {n, x, y, z, e, fn?, c?}}, nameIndex: {name: [id...]}}`

### Modified Files

**`src/client/gmcp_handler.py`**
- Added callbacks: `on_room_actual` (string), `on_room_movimiento` (string)
- Added handlers in `handle()` method:
  - `Room.Actual`: name+exits string for resync
  - `Room.Movimiento`: direction string for incremental tracking
- Added setters: `set_room_actual_callback()`, `set_room_movimiento_callback()`
- Changed `data` parameter type to `Any` (was `Dict[str, Any]`)

**`src/main.py`** (major changes)
- Imports: `MapService`
- `__init__`: instantiate `MapService`, load map, initialize walk tracking variables
- Register GMCP callbacks for `Room.Actual` and `Room.Movimiento`
- `send_command()`: intercept client commands BEFORE MUD send:
  - `locate` → sends "ojear", arms flag, requires connection
  - `irsala <name>` → client-side navigation, no connection needed
  - `parar` → stop current walk, no connection needed
  - Any command → stops walk if in progress
- `_on_mud_data()`: detect locate response (line ending with `[exits]`), parse and announce room
- New callbacks:
  - `_on_room_actual(name_line)` → resync if already localized (no noise on initial connect)
  - `_on_room_movimiento(direction)` → auto-follow: update position, announce room+exits
- New methods:
  - `_handle_irsala(query)` → search, if 1 result walk, else show options
  - `_walk_to(target)` → BFS pathfinding, announce step count, start walk
  - `_walk_next_step()` → send one step, schedule next in 1100ms via `wx.CallLater`
  - `_stop_walk()` → clear walk state, announce

**`src/ui/help_dialog.py`**
- Added "Map" tab to `HELP_CONTENT`:
  - Explains localization (manual "locate" command)
  - Explains automatic tracking (Room.Movimiento GMCP)
  - Explains navigation ("irsala" command)
  - Examples: `locate`, `irsala mercado`, `parar`
  - Note about changing zones
- Updated "Keyboard Map" tab:
  - Added NAVIGATION section with locate, irsala, parar commands

## Data Flow

### Manual Localization

```
User types "locate"
  ↓
send_command("locate") → set _waiting_for_locate=True, send "ojear"
  ↓
MUD responds: "Anduar: Plaza Mayor [n,s,e,o]"
  ↓
_on_mud_data() → detect [exits] pattern
  ↓
find_room() → parse & disambiguate → MapRoom
  ↓
map_service.set_current_room(room_id)
  ↓
announce "Localizado: {room.n}. Salidas: {exits}"
```

### Automatic Position Tracking (After Localized)

```
User moves: "norte" (Alt+8) OR follows: "seguir Fulano"
  ↓
MUD sends GMCP: Room.Movimiento "norte"
  ↓
_on_gmcp() → _on_room_movimiento("norte")
  ↓
map_service.move_by_direction("norte")
  ↓
announce "{new_room.n}. Salidas: {exits}"
```

### Navigation (irsala)

```
User types: "irsala mercado"
  ↓
send_command("irsala mercado") → _handle_irsala("mercado")
  ↓
map_service.search_rooms("mercado")
  ↓
if 1 result: _walk_to(room)
if 0 results: announce "no encontrada"
if 2+ results: announce list, show in output
  ↓
[if walking] _walk_to():
  - find_path() → BFS → [norte, este, norte, ...]
  - set _walk_steps, _walk_index
  - _walk_next_step() [scheduled every 1100ms]
  ↓
Each step: send(direction)
After each step: GMCP Room.Movimiento → announce room
```

### Walk Interruption

```
User types ANY command while walking
  ↓
send_command() → if _walk_steps: _stop_walk()
  ↓
clear _walk_steps, _walk_index
  ↓
announce "Viaje detenido"
  ↓
proceed with new command
```

## Features

✓ **Position Tracking**
- Two-phase: explicit `locate` then automatic GMCP tracking
- `Room.Movimiento` updates on any move (manual or following)
- `Room.Actual` resync if needed (disabled before localization to avoid noise)
- No ambiguous automatic localization (avoid silent drift)

✓ **Room Localization**
- Parse `"Name [exits]"` format from MUD response
- Short name + exit set exact-match disambiguation
- Return None if still ambiguous (better than guessing)
- TTS announcement on successful locate

✓ **Navigation (irsala)**
- Partial name search (case-insensitive substring, max 20 results)
- Single result: auto-walk
- Multiple results: list options, let user refine
- Zero results: announce "no encontrada"

✓ **Pathfinding (BFS)**
- Deque-based BFS over exit graph
- Max 50K visited nodes (guards infinite loops)
- Returns list of MUD commands (e.g., ['norte', 'este', 'norte'])
- Returns None if unreachable

✓ **Auto-Walk Execution**
- Walk scheduled via `wx.CallLater(1100, ...)` — async, non-blocking
- 1100ms delay between steps (same as BlowTorch)
- TTS announcement on walk start (step count)
- Announces each room as you arrive (via Room.Movimiento)
- Stoppable: any user command interrupts and announces "Viaje detenido"

✓ **Room Data**
- 28,816 rooms from Reinos de Leyenda
- 4,073 name index entries (case-folded for lookup)
- Full coordinate system (x, y, z)
- Environment colors (for future visual map)

✓ **Accessibility**
- No visual map in blind mode (follows Phase 1 design)
- All feedback via TTS: room names, exit lists, step counts, status
- TTS uses AudioLevel.MINIMAL for normal movement tracking
- Exit list in natural MUD order (not alphabetical)

## Testing

Verified:
- `python -m py_compile src/models/map_service.py` ✓
- `python test_startup.py` ✓ (all modules load)
- `MapService.load()` → 28816 rooms, 4073 entries ✓
- `find_room()` with real room data ✓
- `search_rooms()` → substring matching ✓
- `move_by_direction()` → position update ✓
- GMCP handler has Room.Actual/Movimiento callbacks ✓
- `main.py` imports MapService and integrates ✓

**Manual testing workflow (when MUD connection available):**
1. Start app: `python src/main.py`
2. Connect: `Ctrl+K` → `reinosdeleyenda.com:23`
3. Localize: type "locate" → hears "Localizado: {room}. Salidas: {exits}"
4. Move: `Alt+8` (north) → hears "{new_room}. Salidas: {exits}"
5. Navigate: type "irsala mercado" → auto-walks, announces each room
6. Interrupt: type any command → hears "Viaje detenido"
7. Follow: type "seguir Fulano" → MUD moves you → auto-announces each room
8. Change zone: type "locate" again → resync to new zone

## Known Limitations

- Map assumes room names are unique enough for disambiguation (if not, returns None)
- No map visualization in blind mode (as designed for accessibility)
- `find_room()` returns None if ambiguous after exit filtering (user must use irsala to refine)
- Walk execution is simple async (no confirmation, no rollback if path becomes blocked)
- No room/path caching (BFS runs every irsala request, but O(N) is acceptable for 28K nodes)
- No multi-zone awareness (player must manually locate when changing zones)

## Next Steps (Future Phases)

- **Phase 4.5**: Add edit UI for custom markers/notes on rooms
- **Phase 5**: Room-aware combat (update combat mode when entering dangerous zone)
- **Phase 6**: Real-world testing with NVDA/JAWS, refinement of TTS timing

## Commits

```
c3c93a4 Phase 4: Add map/navigation system with automatic position tracking
```

## Code Quality

- All syntax verified ✓
- No new external dependencies ✓
- Follows existing patterns (callback architecture, relative imports, MapRoom dataclass) ✓
- Thread-safe (BFS is pure function, walk uses wx.CallLater for UI thread) ✓
- Accessible design (no visual-only feedback, TTS for all state changes) ✓
- Comments only where non-obvious (BFS max nodes guard, two-phase localization) ✓

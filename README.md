# VipZhyla - Accessible MUD Client

An accessible desktop MUD client designed for **blind and visually impaired users**, with screen reader support and keyboard-only navigation.

**🎯 Target:** Blind/visually impaired players on Reinos de Leyenda MUD  
**📝 Status:** Alpha (v0.1.0) - Phase 4 Complete (Map/Navigation)
- ✓ Phase 1: Core Infrastructure (wxPython, keyboard, audio)
- ✓ Phase 2: MUD Connection (Telnet, GMCP, message buffer)
- ✓ Phase 2.5: History Dialogs (Shift+F1-F4)
- ✓ Phase 3: Trigger/Alias/Timer System (with persistence)
- ✓ Phase 4: Map/Navigation (auto-tracking, irsala pathfinding)

**📖 Documentation:** See [CLAUDE.md](CLAUDE.md) for complete architecture and development guide

---

## Features

### Core
- **Accessibility First**: NVDA, JAWS, and Narrator support (wxPython native)
- **Keyboard-Only**: Every function accessible without mouse
- **Text-to-Speech**: pyttsx3 for real-time audio feedback (cross-platform)
- **Cross-Platform**: Windows, macOS, Linux

### Game Features
- **Single-Window Design**: Simplified navigation
- **MUD Connection**: Telnet + GMCP protocol support
- **Message History**: Browse by channel (Shift+F1-F4)
- **Movement**: 12 directional commands (Alt+U/O/I/K + numpad)
- **Automation**: 
  - **Triggers**: Pattern matching with TTS/GAG actions
  - **Aliases**: Command shortcuts (e.g., h→help)
  - **Timers**: Periodic announcements
  - All with JSON persistence
- **Map & Navigation**:
  - Automatic position tracking (follows you as you move)
  - Works when following other players
  - Manual `locate` command
  - Auto-navigate to rooms: `irsala <roomname>`
  - 28,816 room database with pathfinding

## Quick Start

### Prerequisites

- Python 3.11+
- wxPython 4.2.5+
- NVDA (free screen reader for testing)

### Installation

```bash
git clone https://github.com/smiuag/VipZhyla.git
cd VipZhyla
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Running the App

```bash
python src/main.py
```

You'll hear: **"VipZhyla iniciado. Presiona F1 para ayuda, Ctrl+K para conectar."**

### First Steps (Quick Start)

1. **Press F1** → Help system (10 tabs with full documentation)
2. **Press Ctrl+K** → Connect dialog
   - Default: `reinosdeleyenda.com:23`
   - Or enter another MUD server
3. **Type username + password** → Login to MUD
4. **Type `locate`** → Establishes your position (announces room + exits)
5. **Use Alt+U/O/I/K** → Move around (announces each new room automatically)
6. **Type `irsala <roomname>`** → Auto-navigate (e.g., `irsala mercado`)
7. **Press Shift+F1-F4** → Browse message history by channel
8. **Press Ctrl+T** → Manage triggers/aliases/timers (advanced)

## Keybindings (VipZhyla Design)

**Note:** These are VipZhyla's keybindings, inspired by VipMud's accessibility philosophy but optimized for wxPython and WCAG 2.2 standards. See [scripts.md](scripts.md) for original VipMud keybindings (historical reference).

### Movement (QWERTY-Optimized)
- `Alt+U` = West
- `Alt+O` = East
- `Alt+8` = North
- `Alt+K` = South
- `Alt+7/9` = NW/NE
- `Alt+J/L` = SW/SE
- `Alt+I` = Up
- `Alt+M` = Down
- `Alt+,/.` = In/Out

### History & Navigation (Modal Dialogs)
- `Shift+F1` = Channel History
- `Shift+F2` = Room History
- `Shift+F3` = Telepathy History
- `Shift+F4` = Event List
- `Alt+Up/Down` = Previous/Next Message (in history)
- `Alt+Left/Right` = Previous/Next Channel
- `Alt+Home/End` = First/Last Message

### Connection & Management
- `Ctrl+K` = Connect to MUD Server
- `Ctrl+D` = Disconnect
- `F1` = Help (10 tabs: Start, Connection, Movement, Messages, Typing, Triggers, Aliases, Timers, Settings, Keyboard Map)
- `Ctrl+T` = Trigger/Alias/Timer Manager
- `Ctrl+Shift+V` = Toggle Verbosity (normal → verbose)

### Navigation (Commands, Not Keybindings)
- Type `locate` → Establish your position on the map
- Type `irsala <roomname>` → Auto-navigate to a room (BFS pathfinding)
- Type `parar` → Stop current walk

### Global
- `Enter` = Send Command
- `Escape` = Cancel / Close Dialog
- `Tab` = Navigate between fields (in dialogs)

## Architecture

**For architecture and development guidelines, see [CLAUDE.md](CLAUDE.md).**

### Completed Implementation

**Phase 1: Core Infrastructure**
- **`accessibility_core.py`**: wxPython accessibility wrapper (wx.Accessible + MSAA)
- **`keyboard_handler.py`**: Keyboard event routing (24+ keybindings, wxEVT_KEY_DOWN)
- **`audio_manager.py`**: Text-to-speech via pyttsx3 (5 verbosity levels)
- **`main.py`**: Application entry point (wxFrame single-window design)

**Phase 2: MUD Connection**
- **`connection.py`**: Telnet connection, GMCP negotiation
- **`mud_parser.py`**: Parse MUD output into structured messages
- **`message_buffer.py`**: Message history per channel
- **`gmcp_handler.py`**: Structured game data (vitals, room info, channels)

**Phase 2.5: History Dialogs**
- **`list_dialogs.py`**: Accessible modal dialogs (Shift+F1-F4)
- Browse messages by channel with full keyboard navigation

**Phase 3: Automation System**
- **`triggers.py`**: TriggerManager (pattern matching, aliases, timers with JSON persistence)
- **`trigger_dialog.py`**: UI for managing automation (Ctrl+T)
- Actions: TTS announcements, GAG (hide line), extensible design

**Phase 4: Map & Navigation**
- **`map_service.py`**: MapService (28,816 rooms, BFS pathfinding, position tracking)
- Auto-follow via GMCP Room.Movimiento (manual + following support)
- Commands: `locate`, `irsala <room>`, `parar` with 1100ms walk intervals

## Testing the Application

### Screen Reader Testing (Accessibility)

Test with NVDA (free):
```bash
# Download from: https://www.nvaccess.org/download/
# Or on Windows built-in:
Win + Ctrl + Enter  # Start Windows Narrator
```

Enable NVDA, start the app (`python src/main.py`), and verify:
- ✓ Startup announcement: "VipZhyla iniciado..."
- ✓ F1 opens help with 10 readable tabs
- ✓ All dialogs and buttons are readable
- ✓ Status bar at bottom is announced

### Feature Testing Checklist

1. **Connection**
   - [ ] Ctrl+K opens connection dialog
   - [ ] Default is `reinosdeleyenda.com:23`
   - [ ] Ctrl+D disconnects after connecting

2. **Movement**
   - [ ] Alt+8 sends "north" to MUD
   - [ ] Alt+U/O/I/K send west/east/up/down
   - [ ] Movement echoes in output: `> north`

3. **History (Shift+F1-F4)**
   - [ ] Shift+F1 opens channel history
   - [ ] Up/Down arrow navigate messages
   - [ ] Alt+Left/Right switch channels
   - [ ] Escape closes dialog

4. **Map & Navigation**
   - [ ] Type `locate` → announces "Localizado: {room}"
   - [ ] Move → announces each new room automatically
   - [ ] Type `irsala mercado` → auto-navigates (1100ms per step)
   - [ ] Type `parar` → stops walk with announcement

5. **Help**
   - [ ] F1 opens help
   - [ ] 10 tabs navigate with Tab key
   - [ ] Escape closes help

6. **Automation (Ctrl+T)**
   - [ ] Ctrl+T opens manager dialog (3 tabs: Triggers, Aliases, Timers)
   - [ ] Can view items (not yet editable - Phase 3.5)

## Development Workflow

See [CLAUDE.md](CLAUDE.md) for complete development guide including:
- Setup commands (venv, pip install)
- Running the app (`python src/main.py`)
- Testing with pytest
- Code quality tools
- Accessibility checklist

### Quick Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_keyboard.py::test_keyboard_handler_init

# Run with coverage
pytest tests/ --cov=src
```

### Accessibility Checklist Before Commit

- [ ] NVDA reads all text correctly
- [ ] All controls keyboard-accessible
- [ ] No visual-only feedback
- [ ] Tab order is logical
- [ ] Tests pass: `pytest tests/`
- [ ] No new console warnings

See [accesibilidad.md](accesibilidad.md) for detailed accessibility principles and implementation patterns.

### Running Tests

```bash
# Verify all modules load
python test_startup.py

# Run unit tests
pytest tests/ -v

# Run specific test
pytest tests/test_triggers.py -v
```

## Troubleshooting

**Problem:** "No module named 'wxPython'"
```bash
pip install --user wxPython pyttsx3
```

**Problem:** Map won't load
```bash
# Check file exists
ls src/data/map-reinos.json
```

**Problem:** Screen reader not reading content
- [ ] Is NVDA running? (Ctrl+Alt+N)
- [ ] Is app focused? (click window or press Alt+Tab)
- [ ] Try pressing Ctrl+Home to focus main content

**Problem:** Can't type commands
- [ ] Make sure Input field has focus (visible in status)
- [ ] Press Tab until focused on Input field

## Feedback & Issues

This is **Alpha** software. Expect bugs and incomplete features.

If testing:
1. Note what you tried (commands, keybindings)
2. What you expected to happen
3. What actually happened
4. Which screen reader (NVDA, JAWS, etc.)

## Documentation Hub

| Document | Purpose | Read If |
|----------|---------|---------|
| **[CLAUDE.md](CLAUDE.md)** | Architecture, development guide, project status | You're developing or contributing code |
| **[accesibilidad.md](accesibilidad.md)** | Accessibility principles (WCAG 2.2 + ChannelHistory) | You're implementing UI or unsure about accessibility |
| **[scripts.md](scripts.md)** | VipMud game reference (channels, classes, routes) | You're implementing game-specific features |
| **[docs/mushclient_reference.md](docs/mushclient_reference.md)** | MushClient accessibility research | You want to understand existing blind-accessible clients |

**Quick navigation:** See [CLAUDE.md](CLAUDE.md) for a complete documentation hub with reading order by development phase.

## License

MIT - See [LICENSE](LICENSE) for details

## Contributing

Contributions welcome! Please:

1. Test with NVDA before submitting PR
2. Follow the accessibility checklist
3. Document keybindings changes
4. Add tests for new features

## References & Inspiration

- **VipMud Scripts** (Reinos de Leyenda): [ScriptsRL](https://github.com/DPrenC/ScriptsRL) — Original MUD scripts for game mechanics reference
- **ChannelHistory**: [ironcross32/ChannelHistory](https://github.com/ironcross32/ChannelHistory) — Accessible Mudlet channel management (accessibility patterns)
- **MushClient**: [nickgammon/mushclient](https://github.com/nickgammon/mushclient) — Windows MUD client with blind player support
- **Oracle System**: [achaea-oracle/oracle](https://github.com/achaea-oracle/oracle) — Blind accessibility framework for Achaea MUD
- **WCAG 2.2 Guidelines**: [w3.org/TR/WCAG22](https://www.w3.org/TR/WCAG22/) — Web accessibility standards (principles apply to desktop)

## Contributing

1. Test with NVDA before submitting PR
2. Follow the accessibility checklist
3. Document keybinding changes in [CLAUDE.md](CLAUDE.md)
4. Add tests for new features
5. Read [accesibilidad.md](accesibilidad.md) before implementing UI

---

**Last Updated**: 2026-04-23  
**Version**: 0.1.0 (Alpha)  
**License**: MIT

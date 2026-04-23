# VipZhyla - Accessible MUD Client

An accessible desktop MUD client designed for **blind and visually impaired users**, with screen reader support and keyboard-only navigation.

**🎯 Target:** Blind/visually impaired players on Reinos de Leyenda MUD  
**📝 Status:** Alpha (v0.1.0) - Core Infrastructure Mostly Complete, Phase 2 Priority  
**📖 Documentation:** See [CLAUDE.md](CLAUDE.md) for complete architecture and development guide

---

## Features

- **Accessibility First**: NVDA, JAWS, and Narrator support (wxPython native)
- **Keyboard-Only**: Every function accessible without mouse
- **Text-to-Speech**: pyttsx3 for audio feedback (cross-platform)
- **Cross-Platform**: Windows, macOS, Linux
- **Single-Window Design**: Simplified navigation
- **Modal Dialogs**: History browsing (Shift+F1-F4)
- **VipZhyla-Inspired Design**: Accessibility-first approach based on VipMud philosophy

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

### Global
- `Enter` = Send Command
- `Escape` = Cancel / Close Dialog
- `Ctrl+Shift+V` = Toggle Verbose Mode (silence → minimal → normal → verbose → debug)

## Architecture

**For architecture and development guidelines, see [CLAUDE.md](CLAUDE.md).**

### Current Implementation (Phase 1)

- **`accessibility_core.py`**: wxPython accessibility wrapper (wx.Accessible + MSAA)
- **`keyboard_handler.py`**: Keyboard event routing (24+ keybindings, wxEVT_KEY_DOWN)
- **`audio_manager.py`**: Text-to-speech via pyttsx3 (5 verbosity levels: silent→debug)
- **`main.py`**: Application entry point (wxFrame single-window design)

### Phase 2 (In Progress)

- **`client/connection.py`**: MUD server connection (telnetlib)
- **`client/telnet_protocol.py`**: Telnet protocol handling
- **`client/mud_parser.py`**: Parse MUD output
- **`client/message_buffer.py`**: Message history per channel

## Accessibility Testing

Test with NVDA (free):

```bash
# Download from: https://www.nvaccess.org/download/
# Or on Windows built-in:
Win + Ctrl + Enter
```

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

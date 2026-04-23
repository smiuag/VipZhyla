# VipZhyla - Accessible MUD Client

An accessible desktop MUD client designed for **blind and visually impaired users**, with screen reader support and keyboard-only navigation.

## Features

- **Accessibility First**: NVDA, JAWS, and Narrator support
- **Keyboard-Only**: Every function accessible without mouse
- **Text-to-Speech**: pyttsx3 for audio feedback
- **Cross-Platform**: Windows, macOS, Linux
- **Single-Window Design**: Simplified navigation
- **Modal Dialogs**: History browsing (Shift+F1-F4)

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

## Keybindings

### Movement (VipMud-inspired QWERTY)
- `Alt+U` = West
- `Alt+O` = East
- `Alt+8` = North
- `Alt+K` = South
- `Alt+7/9` = NW/NE
- `Alt+J/L` = SW/SE
- `Alt+I` = Up
- `Alt+M` = Down
- `Alt+,/.` = In/Out

### History & Navigation
- `Shift+F1` = Channel History
- `Shift+F2` = Room History
- `Shift+F3` = Telepathy History
- `Shift+F4` = Event List
- `Alt+Up/Down` = Previous/Next Message
- `Alt+Left/Right` = Previous/Next Channel
- `Alt+Home/End` = First/Last Message

### Other
- `Enter` = Send Command
- `Escape` = Cancel
- `Ctrl+Shift+V` = Toggle Verbose Mode

## Architecture

See [CLAUDE.md](CLAUDE.md) for architecture and development guidelines.

### Core Modules

- **`accessibility_core.py`**: wxPython accessibility wrapper (wx.Accessible)
- **`keyboard_handler.py`**: Keyboard event routing
- **`audio_manager.py`**: Text-to-speech and audio events
- **`main.py`**: Application entry point

## Accessibility Testing

Test with NVDA (free):

```bash
# Download from: https://www.nvaccess.org/download/
# Or on Windows built-in:
Win + Ctrl + Enter
```

## Development

### Testing

```bash
pytest tests/
```

### Accessibility Checklist Before Commit

- [ ] NVDA reads all text correctly
- [ ] All controls keyboard-accessible
- [ ] No visual-only feedback
- [ ] Tab order is logical
- [ ] Tests pass

See [accesibilidad.md](accesibilidad.md) for detailed accessibility guidelines.

## Documentation

- **[CLAUDE.md](CLAUDE.md)** — Architecture and development guide
- **[accesibilidad.md](accesibilidad.md)** — Accessibility guidelines (WCAG 2.2 + ChannelHistory patterns)
- **[scripts.md](scripts.md)** — Reference for MUD game mechanics

## License

MIT - See [LICENSE](LICENSE) for details

## Contributing

Contributions welcome! Please:

1. Test with NVDA before submitting PR
2. Follow the accessibility checklist
3. Document keybindings changes
4. Add tests for new features

## Community

- **Original VipMud Scripts**: [ScriptsRL](https://github.com/DPrenC/ScriptsRL)
- **Accessibility Reference**: [ChannelHistory](https://github.com/ironcross32/ChannelHistory)
- **WCAG Guidelines**: [WCAG 2.2](https://www.w3.org/TR/WCAG22/)

---

**Status**: Alpha (v0.1.0) - Early Development

**Target**: Blind and visually impaired MUD players who need an accessible client

**Last Updated**: 2026-04-23

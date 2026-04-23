# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**VipZhyla** is a desktop MUD client application being developed for **blind and visually impaired users**. It's designed to be similar to Mudlet or VipMud but with accessibility as the **primary goal**.

### Key Principles

- **Accessibility First:** Screen reader support, keyboard-only navigation, audio feedback
- **Visual Secondary:** GUI is provided for development and sighted users, but not required for functionality
- **Target Users:** Blind/visually impaired MUD players who need an accessible client
- **Inspiration:** VipMud (VipZhyla scripts), Mudlet, ChannelHistory accessibility patterns

---

## Core Development Files

### Accessibility & Design

- **[accesibilidad.md](accesibilidad.md)** — Complete accessibility guidelines (WCAG 2.2 + ChannelHistory patterns)
  - Read this FIRST before implementing any UI
  - Keyboard navigation standards
  - Screen reader integration
  - Audio feedback patterns
  
- **[scripts.md](scripts.md)** — Reference for VipZhyla MUD scripts (Reinos de Leyenda)
  - Use when adding MUD-specific features
  - Game mechanics, classes, keybindings
  - Structure of existing MUD scripts

### Scripts Folder

- **[Scripts/](Scripts/)** — Complete VipZhyla MUD scripts
  - 1700+ files for the Reinos de Leyenda MUD
  - Use `scripts.md` as index (don't browse manually)
  - Reference for MUD client features to implement

---

## Architecture

### Technology Stack (To Be Decided)

**Options to consider:**
- **Python** (PyQt5/PySide2) — Fast development, good accessibility APIs
- **Electron** (JS/React) — Cross-platform, but web-based (accessibility testing needed)
- **C# WPF** (Windows) — Native accessibility APIs (Windows only)
- **Qt** (C++/PyQt) — Strong accessibility, cross-platform

**Decision factors:**
- Screen reader support maturity
- Keyboard-first input handling
- Cross-platform requirements
- Development speed

### Application Structure (Proposed)

```
VipZhyla/
├── src/
│   ├── app/
│   │   ├── main.py                  # App entry point
│   │   ├── accessibility_core.py    # Screen reader API wrapper
│   │   ├── keyboard_handler.py      # Keyboard navigation engine
│   │   └── audio_manager.py         # Sound & TTS management
│   │
│   ├── ui/
│   │   ├── main_window.py           # Main GUI (secondary)
│   │   ├── output_display.py        # Text output (visual + accessible)
│   │   ├── input_field.py           # Command input
│   │   └── status_bar.py            # Status display
│   │
│   ├── client/
│   │   ├── connection.py            # MUD server connection
│   │   ├── telnet_protocol.py       # Telnet implementation
│   │   ├── mud_parser.py            # Parse MUD output
│   │   └── message_buffer.py        # Message history
│   │
│   └── models/
│       ├── character.py             # Player character data
│       ├── channel.py               # Message channels (Bando, Telepátia, etc.)
│       └── triggers.py              # Trigger/alias system
│
├── tests/
│   ├── test_accessibility.py        # Screen reader compatibility
│   ├── test_keyboard_nav.py         # Keyboard navigation
│   └── test_mud_parsing.py          # MUD output parsing
│
├── docs/
│   ├── ACCESSIBILITY.md             # [symlink to accesibilidad.md]
│   ├── SCRIPTS_REFERENCE.md         # [symlink to scripts.md]
│   └── ARCHITECTURE.md              # Design decisions
│
├── CLAUDE.md                        # This file
└── README.md                        # User guide (to write)
```

---

## Development Phases

### Phase 1: Core Infrastructure (NOW)
- [ ] Choose technology stack
- [ ] Implement accessibility core (screen reader API wrapper)
- [ ] Implement keyboard navigation engine
- [ ] Basic TTS/audio system
- [ ] Test with NVDA/JAWS

### Phase 2: Basic MUD Connection
- [ ] Telnet protocol implementation
- [ ] Server connection/disconnection
- [ ] Basic text reception and display
- [ ] Character management (login, character select)

### Phase 3: Message Handling
- [ ] Channel system (Bando, Telepátia, Sala, etc.)
- [ ] Message history and navigation
- [ ] Filtering and categorization
- [ ] Audio triggers for events

### Phase 4: Advanced Features
- [ ] Trigger/alias system
- [ ] Macro management
- [ ] Combat assistance (health tracking, etc.)
- [ ] Map/navigation support

### Phase 5: Polish & Testing
- [ ] Screen reader testing (NVDA, JAWS, Narrator)
- [ ] Keyboard-only workflow validation
- [ ] Performance optimization
- [ ] Documentation

---

## Accessibility Standards (Must Follow)

### From WCAG 2.2 + ChannelHistory:

**Keyboard Navigation:**
```
Alt + [Letter]             → Main functions
Alt + Shift + [Letter]     → Extended functions
Ctrl + [Letter]            → Global commands
Alt + [Arrow keys]         → Navigation (up/down, left/right)
Alt + Home/End             → Jump to start/end
```

**Screen Reader Integration:**
- Use native Windows Accessibility API (UI Automation) on Windows
- Test with NVDA, JAWS, and Narrator
- Announce all state changes
- Clear, descriptive labels for all controls

**Audio Feedback:**
- No GUI-only feedback (colors, visual indicators)
- All important events have audio/text equivalent
- Configurable verbosity (verbose/expert modes)

**No Mouse Required:**
- Every feature must work with keyboard only
- No mouse gestures or hover-only buttons
- Tab navigation works predictably

See **[accesibilidad.md](accesibilidad.md)** for complete guidelines.

---

## MUD Integration (Reference)

The existing **Scripts/** folder contains:
- Game mechanics, classes, abilities
- Keybinding patterns (Alt+X for combat, etc.)
- Channel structure (Bando, Telepátia, Sala, Gremio, etc.)
- Message formatting

See **[scripts.md](scripts.md)** for quick reference.

**When implementing:**
1. Mirror existing VipMud keybindings where possible
2. Study Alias_Macros.set for standard patterns
3. Implement channel system (Clases/Paths/Ambientacion as reference)
4. Follow combat mode paradigm (Original/Combat/XP/Idle)

---

## Testing Requirements

### Accessibility Testing

- [ ] Test with NVDA (free screen reader)
  ```bash
  https://www.nvaccess.org/download/
  ```
- [ ] Test with Windows Narrator
  ```bash
  Win + Ctrl + Enter
  ```
- [ ] Test with JAWS (if available)
- [ ] Keyboard-only: Disable mouse/touchpad, complete workflows

### Functional Testing

- [ ] Connect to MUD server
- [ ] Receive and display text
- [ ] Send commands
- [ ] Navigate message history
- [ ] Filter channels
- [ ] Trigger/alias system

### Code Quality

- [ ] Unit tests for core modules
- [ ] Integration tests for MUD communication
- [ ] Accessibility assertions in tests
- [ ] No console errors when screen reader attached

---

## Development Workflow

### When Starting New Feature

1. **Read accesibilidad.md** for accessibility requirements
2. **Implement keyboard handler first** (before GUI)
3. **Add screen reader announcements** alongside visual updates
4. **Test with NVDA before** visual styling
5. **Document keybindings** in code and CLAUDE.md

### Before Committing

- [ ] Screen reader still works (Narrator test)
- [ ] All controls keyboard-accessible
- [ ] No visual-only feedback
- [ ] Code documented
- [ ] Tests pass

### Code Style

- Use clear, descriptive variable names
- Comment non-obvious accessibility code
- Centralize keybinding definitions
- Keep UI code separate from accessibility code

---

## Tools & References

### Screen Readers
- **NVDA** (Windows, free): https://www.nvaccess.org/
- **Narrator** (Windows built-in): Win + Ctrl + Enter
- **JAWS** (Windows, commercial): https://www.freedomscientific.com/

### Accessibility APIs
- **Windows UI Automation**: Microsoft.UIAutomation
- **AT-SPI2** (Linux): Assistive Technology Service Provider Interface
- **NSAccessibility** (macOS): Apple Accessibility API

### Python Libraries (If using Python)
- `pyautogui` — Keyboard input handling
- `pyttsx3` — Text-to-speech
- `pyperclip` — Clipboard access
- `accessible-output2` — Screen reader integration (legacy, check alternatives)
- `comtypes` — Windows API access

### Documentation
- [accesibilidad.md](accesibilidad.md) — Complete accessibility guidelines
- [scripts.md](scripts.md) — VipZhyla MUD reference
- [WCAG 2.2](docs/WCAG2.2/wcag22-full.html) — Web accessibility (principles apply)
- [ChannelHistory](https://github.com/ironcross32/ChannelHistory) — Production accessibility example

---

## Next Steps

1. **Decide technology stack** (Python/Qt/Electron/C#)
2. **Set up project structure** (src/, tests/, docs/)
3. **Implement accessibility core** (keyboard + TTS wrapper)
4. **Test with NVDA** (before building UI)
5. **Iteratively add features** (connection → text display → channels → triggers)

---

## Questions to Answer Before Development

- What's the primary target OS? (Windows / Linux / macOS / Cross-platform?)
- Python or compiled language?
- How closely should we mirror VipMud keybindings?
- Should we support Reinos de Leyenda MUD initially, or generic MUD clients?
- Single-window or multi-window design?

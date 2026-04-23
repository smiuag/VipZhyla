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

## Documentation Hub

This project has multiple documentation files. Here's what each one is for and when to read it:

### 🎯 Quick Navigation (By Task)

| Task | Read This | Why |
|------|-----------|-----|
| **Starting development** | CLAUDE.md → accesibilidad.md | Architecture overview + accessibility requirements |
| **Implementing new UI widget** | accesibilidad.md → CLAUDE.md (Key Modules) | WCAG 2.2 principles + code structure patterns |
| **Understanding VipMud inspiration** | scripts.md | Historical reference for game mechanics/keybindings |
| **Understanding MushClient patterns** | docs/mushclient_reference.md | Blind accessibility research (Oracle system, scrollback, triggers) |
| **User features & keybindings** | README.md | What the app does and how to use it |
| **Deploying/publishing** | README.md + accesibilidad.md | Installation guide + accessibility checklist |

### 📚 Full Documentation Reference

#### **[README.md](README.md)** — User Guide & Getting Started
- **Purpose:** User-facing documentation for installation and usage
- **Read if:** You want to understand features, keybindings, or install the app
- **Contains:**
  - Feature overview (Accessibility First, Keyboard-Only, TTS)
  - Quick start (installation, running the app)
  - Complete keybinding reference (movement, history, navigation)
  - Accessibility testing instructions (NVDA/Narrator)
  - Contributing guidelines
- **DO NOT read for:** Architecture, implementation details, development workflow

#### **[accesibilidad.md](accesibilidad.md)** — Accessibility Standards & Patterns (WCAG 2.2 + ChannelHistory)
- **Purpose:** Comprehensive accessibility guide for implementing blind-friendly features
- **Read if:** Before implementing ANY UI, or when unsure about accessibility requirements
- **Contains:**
  - WCAG 2.2 four principles (Perceivable, Operable, Understandable, Robust)
  - ChannelHistory patterns (category navigation, TTS announcements, timestamps)
  - Implementation checklist (5 tests before publishing)
  - wxPython-specific accessibility code examples
  - Advanced patterns (context stack, incremental search, state change detection)
- **Key reference:** This is your ACCESSIBILITY BIBLE—patterns here must be followed in all UI
- **DO NOT read for:** How to run tests, project setup, VipMud scripting

#### **[scripts.md](scripts.md)** — VipMud Scripts Reference (Reinos de Leyenda)
- **Purpose:** Index of VipMud scripts for understanding game mechanics and inspiration
- **Read if:** You need to understand Reinos de Leyenda classes, keybindings, channels, or locations
- **Contains:**
  - Complete directory structure of VipMud scripts (1700+ files)
  - Core script files (Alias_Macros, Combat, Comunicaciones, Movimiento, Modos, etc.)
  - Class templates (Soldados, Khazads, Paladines, etc.)
  - Location routes (Takome, Eldor, Golthur, etc.)
  - Regional scripts (Anduar, Dendra, Takome, etc.)
  - Profession/trade scripts (Minero, Herrero, Marinero)
  - Sound files organization
  - Original VipMud keybindings (F7, F10, F11, F12, Alt+0-9, etc.)
  - Troubleshooting guide
- **⚠️ IMPORTANT:** These are VipMud's OLD keybindings. VipZhyla uses NEW keybindings (Alt+U/O/I/K). Consult scripts.md for **game mechanics inspiration only**, not for client keybinding design.
- **DO NOT read for:** UI implementation, accessibility standards, VipZhyla development workflow

#### **[CLAUDE.md](CLAUDE.md)** — Development Guide (This File!)
- **Purpose:** Architecture, development phases, and coding guidelines for Claude Code
- **Read if:** You're starting development or need to understand the codebase
- **Contains:**
  - Project overview and key principles
  - Technology stack decision (wxPython) with rationale
  - Application structure (src/, tests/, docs/)
  - Development phases (Phase 1-5)
  - Accessibility standards (keyboard, screen readers, audio)
  - MUD integration reference
  - Development commands (run, test, lint)
  - Development workflow and wxPython checklist
  - Key modules explanation (accessibility_core, keyboard_handler, audio_manager, main)
  - Current project status (Phase 1 complete, Phase 2 priorities)
- **DO NOT read for:** User features, game mechanics, WCAG detailed principles

#### **[docs/mushclient_reference.md](docs/mushclient_reference.md)** — MushClient Accessibility Research
- **Purpose:** Reference implementation study for blind-accessible MUD clients
- **Read if:** You want to understand existing accessibility patterns or design advanced features
- **Contains:**
  - MushClient overview (Windows C++ client, 96.7% C++)
  - Core features (500K scrollback, triggers, aliases, timers)
  - Lua scripting system (5.1 runtime)
  - Accessibility for blind users (MushReader plugin, Oracle system for Achaea)
  - Oracle system architecture (blind player framework)
  - Technical architecture and dependencies
  - Comparison with VipZhyla approach
  - Design patterns worth adopting (plugin architecture, scrollback buffer, trigger system)
  - Blind user testimonies and community feedback
- **Key takeaway:** Oracle's modular channel organization and audio feedback patterns are inspiration for Phase 3+
- **DO NOT read for:** Current project status, VipZhyla-specific implementation

### 📁 Core Development Files

- **[Scripts/](Scripts/)** — Complete VipZhyla MUD scripts (1700+ files)
  - Use `scripts.md` as index (don't browse manually)
  - Reference for MUD client features to implement (game mechanics, channels)
  - ⚠️ VipMud configuration—not VipZhyla configuration

---

## Documentation Consistency Notes

### ✅ Aligned Across Docs

| Aspect | Status | Evidence |
|--------|--------|----------|
| **Technology Stack** | ✅ Consistent | wxPython 4.2.5+ in CLAUDE.md, README.md, accesibilidad.md, requirements.txt |
| **Audio/TTS** | ✅ Consistent | pyttsx3 recommended in accesibilidad.md, implemented in audio_manager.py, README.md mentions it |
| **Accessibility Standards** | ✅ Consistent | WCAG 2.2 + ChannelHistory in accesibilidad.md, referenced in CLAUDE.md, followed in code |
| **VipMud Inspiration** | ✅ Consistent | Referenced in CLAUDE.md, detailed in scripts.md, used for game mechanics |
| **Screen Readers** | ✅ Consistent | NVDA-first approach in CLAUDE.md, testing guide in accesibilidad.md and README.md |
| **Single-Window Design** | ✅ Consistent | CLAUDE.md architecture, README.md features, main.py implementation |
| **Target Audience** | ✅ Consistent | Blind/visually impaired users in all docs |

### ⚠️ Potential Confusion Points (CLARIFIED)

#### 1. **Keybindings: Old vs. New**
- **scripts.md** contains VipMud's keybindings (F7, F10, F11, F12, Alt+0-9) — these are from the ORIGINAL VipMud client
- **CLAUDE.md & README.md** define VipZhyla's NEW keybindings (Alt+U/O/I/K for movement, Shift+F1-F4 for histories)
- **Clarification:** We are NOT copying VipMud's keybindings 1:1. We are **inspired by** VipMud's approach (accessibility-first, keyboard-driven) but designing NEW keybindings optimized for wxPython and WCAG standards
- **When to use each:** 
  - Use scripts.md to understand VipMud's **design philosophy** (keyboard-first, channel organization)
  - Use README.md/CLAUDE.md for VipZhyla's **actual keybindings**

#### 2. **Accesibilidad.md: General vs. Project-Specific**
- **accesibilidad.md** is a COMPREHENSIVE GUIDE to accessible desktop app design. It's not just for VipZhyla—it's general knowledge applicable to any app.
- **CLAUDE.md** applies accesibilidad.md principles specifically to VipZhyla (wxPython, NVDA focus, etc.)
- **When to use:** Read accesibilidad.md for the PRINCIPLES; read CLAUDE.md for how we apply them

#### 3. **Scripts/ Folder: Reference Only**
- **scripts.md** is an INDEX to Scripts/
- **Scripts/** contains 1700+ VipMud configuration files
- These are from the original VipMud client for Reinos de Leyenda—NOT VipZhyla configuration files
- **Current use:** Reference for understanding game mechanics, channels (Bando, Telepátia), regions, classes
- **Future use (Phase 3+):** May inspire trigger/alias/timer system design, but VipZhyla will have its own Python-based implementation
- **When to use:** When implementing features like channel filtering, map system, or combat modes

#### 4. **MushClient Reference: Historical Research**
- **docs/mushclient_reference.md** is a study of MushClient (another accessible MUD client)
- **Purpose:** Learn from an existing accessible MUD client implementation (Oracle system, Lua scripting, 500K scrollback)
- **Not a requirement:** We're not building MushClient, just learning from its accessibility patterns
- **Specific inspiration:**
  - Oracle's channel organization (Phase 3 inspiration)
  - Scrollback buffer design (Phase 2 implementation)
  - Plugin architecture philosophy (may inform Phase 5 scripting system)

### 📋 Document Reading Order (By Development Phase)

**Phase 1 (Core Infrastructure):**
1. CLAUDE.md (overview + key modules)
2. accesibilidad.md (WCAG 2.2 principles before UI work)
3. README.md (keybindings you're implementing)

**Phase 2 (MUD Connection):**
1. scripts.md (understand game channels and data flow)
2. docs/mushclient_reference.md (scrollback buffer design)
3. CLAUDE.md (Phase 2 requirements)

**Phase 3 (Trigger/Alias System):**
1. scripts.md (understand VipMud triggers/aliases)
2. docs/mushclient_reference.md (Lua trigger patterns)
3. accesibilidad.md (keyboard shortcuts for new features)

**Phase 4 (Map/Navigation):**
1. scripts.md (Paths/ folder for route structure)
2. docs/mushclient_reference.md (map system inspiration)

---

## Architecture

### Technology Stack (DECIDED: wxPython)

**Chosen: Python + wxPython**

**Rationale (based on real-world accessibility testing):**
- **NVDA itself uses wxPython** for its dialogs/preferences — maximum validation
- **Better JAWS/Narrator compatibility** than Qt (documented issues with Qt 5.11+)
- **Proven accessibility** in production (not just documentation)
- **Cross-platform native widgets** (Windows, macOS, Linux)
- **Active maintenance** (4.2.5+ in 2026)
- **Lighter weight** (~80MB vs ~150MB for Qt)

**Trade-offs:**
- macOS VoiceOver support is less mature than Qt (acceptable for Windows-heavy user base)
- Smaller community than Qt, but active accessibility discussions
- Requires explicit accessibility implementation (like all frameworks)

### Application Structure (wxPython)

```
VipZhyla/
├── src/
│   ├── app/
│   │   ├── main.py                  # App entry point
│   │   ├── accessibility_core.py    # wxPython Accessibility wrapper
│   │   │                             # (wraps wx.Accessible, MSAA APIs)
│   │   ├── keyboard_handler.py      # Keyboard navigation engine
│   │   └── audio_manager.py         # Sound & TTS management (pyttsx3)
│   │
│   ├── ui/
│   │   ├── main_window.py           # wxFrame main window (single-window)
│   │   ├── output_panel.py          # wx.Panel for text output
│   │   ├── input_panel.py           # wx.Panel for command input
│   │   ├── status_panel.py          # wx.Panel for status/info
│   │   └── list_dialogs.py          # Modal wx.Dialog for histories
│   │
│   ├── client/
│   │   ├── connection.py            # MUD server connection (telnetlib)
│   │   ├── telnet_protocol.py       # Telnet implementation
│   │   ├── mud_parser.py            # Parse MUD output
│   │   └── message_buffer.py        # Message history (channels)
│   │
│   └── models/
│       ├── character.py             # Player character data
│       ├── channel.py               # Message channels (Bando, Telepátia, etc.)
│       └── triggers.py              # Trigger/alias system
│
├── tests/
│   ├── test_accessibility.py        # NVDA/JAWS/Narrator compatibility
│   ├── test_keyboard_nav.py         # Keyboard navigation
│   ├── test_mud_parsing.py          # MUD output parsing
│   └── test_wx_widgets.py           # wxPython widget accessibility
│
├── docs/
│   ├── ACCESSIBILITY.md             # [symlink to accesibilidad.md]
│   ├── SCRIPTS_REFERENCE.md         # [symlink to scripts.md]
│   └── ARCHITECTURE.md              # wxPython accessibility decisions
│
├── CLAUDE.md                        # This file
└── README.md                        # User guide (to write)
```

---

## Development Phases

### Phase 1: Core Infrastructure (MOSTLY COMPLETE)
- [x] Choose technology stack → wxPython 4.2.5+
- [x] Implement accessibility core (screen reader API wrapper) → `src/app/accessibility_core.py`
- [x] Implement keyboard navigation engine → `src/app/keyboard_handler.py`
- [x] Basic TTS/audio system → `src/app/audio_manager.py`
- [ ] Test with NVDA/JAWS (ongoing)

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

### From WCAG 2.2 + ChannelHistory (wxPython Implementation):

**Keyboard Navigation (VipMud-inspired):**
```
Alt + U/O/I/K/J/L/Y/7/8/9  → Directions (QWERTY movement)
Alt + [Letter]             → Main functions
Alt + Shift + [Letter]     → Extended functions
Ctrl + [Letter]            → Global commands
Alt + Home/End             → Jump to start/end
Shift+F1-F4               → History lists (modal dialogs)
```

**Screen Reader Integration (wxPython):**
- Implement `wx.Accessible` for all custom widgets
- Set `SetName()` on all controls (labels for screen readers)
- Set `SetDescription()` for complex controls
- Use `wx.NewIdRef()` for accessible event handling
- Test with NVDA first (NVDA uses wxPython), then JAWS/Narrator

**Audio Feedback:**
- No GUI-only feedback (colors, visual indicators)
- TTS announcements via `pyttsx3` for all state changes
- Configurable verbosity (verbose/expert modes)
- Sound events for important game actions

**No Mouse Required:**
- Every feature works with keyboard only
- No mouse gestures or hover-only buttons
- Tab navigation works predictably through all panels

**Known wxPython Limitations:**
- macOS VoiceOver support is incomplete (acceptable for Windows-heavy user base)
- Status bar not fully accessible on macOS
- Focus testing required after UI changes

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

## Development Commands

### Setup & Environment

```bash
# Initial setup
python -m venv venv
source venv/bin/activate    # macOS/Linux
# or: venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Running the App

```bash
# Start the application
python src/main.py

# With verbose audio output
python src/main.py --verbose

# Enable debug mode (extra logging)
python src/main.py --debug
```

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_keyboard.py

# Run single test function
pytest tests/test_keyboard.py::test_keyboard_handler_init

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

### Code Quality

```bash
# Format code (if using black)
black src/ tests/

# Type checking (if using mypy)
mypy src/
```

---

## Development Workflow

### When Starting New Feature

1. **Read accesibilidad.md** for accessibility requirements
2. **Create wxPython widget with SetName/SetDescription**
3. **Implement keyboard handler** (wxEVT_KEY_DOWN)
4. **Add TTS announcements** via audio_manager.py
5. **Test with NVDA** (Windows) before visual tweaks
6. **Write tests** in tests/ before implementation
7. **Document keybindings** in code and CLAUDE.md

### wxPython-Specific Checklist

- [ ] Control has `SetName()` with descriptive label
- [ ] Complex controls have `SetDescription()`
- [ ] `wx.Accessible` subclass created if custom widget
- [ ] All keyboard events handled via wxEVT_KEY_DOWN
- [ ] Tab order is logical (use `SetTabOrder()` if needed)
- [ ] Focus indicators work without visual-only cues
- [ ] TTS announces all state changes
- [ ] NVDA reads all text correctly

### Before Committing

- [ ] NVDA reads widget correctly
- [ ] All controls keyboard-accessible
- [ ] No visual-only feedback
- [ ] Code documented with docstrings
- [ ] Tests pass: `pytest tests/`
- [ ] No new console warnings

### Code Style

- Use clear, descriptive variable names
- Comment wxPython accessibility code
- Centralize keybinding definitions in `keyboard_handler.py`
- Keep UI code separate from accessibility (use accessibility_core.py)
- Prefix custom wx widgets with `Accessible` (e.g., `AccessibleTextCtrl`)
- Add docstrings to public methods

---

## Key Modules (Phase 1 Implementation)

### src/app/accessibility_core.py (267 lines)
Base classes for accessible wxPython widgets:
- **AccessibleControl** — Mixin for SetAccessibleName/SetAccessibleDescription
- **AccessiblePanel** — Panel with MakeAccessible() helper
- **AccessibleTextCtrl** — Text control with accessibility support

**Use for:** Creating new UI widgets with built-in screen reader support

### src/app/keyboard_handler.py (217 lines)
Keyboard navigation engine with 24+ keybindings:
- **KeyAction enum** — Movement, history navigation, global commands
- **KeyboardHandler** — Register callbacks, route wxEVT_KEY_DOWN events
- **VipMud-inspired keybindings** — Alt+U/O/I/K for directions, Shift+F1-F4 for histories

**Use for:** Handling all keyboard input, adding new keybindings

### src/app/audio_manager.py (198 lines)
Text-to-speech and audio event management:
- **AudioLevel enum** — SILENT, MINIMAL, NORMAL, VERBOSE, DEBUG
- **AudioManager** — Thread-safe TTS announcements, state/event/error announcements
- **pyttsx3 integration** — Cross-platform speech synthesis

**Use for:** Announcing UI changes, state updates, game events, errors

### src/main.py (205 lines)
Application entry point with single-window design:
- **VipZhylaApp** — wx.App initialization (keyboard + audio handlers)
- **MainWindow** — wx.Frame with output/input/status panels
- **Event handling** — Keyboard routing, command sending, output display

**Use for:** Starting the app, understanding main window layout

---

## Tools & References

### Screen Readers
- **NVDA** (Windows, free): https://www.nvaccess.org/
- **Narrator** (Windows built-in): Win + Ctrl + Enter
- **JAWS** (Windows, commercial): https://www.freedomscientific.com/

### Accessibility APIs (wxPython Integration)

**Windows:**
- **MSAA/UI Automation** — wxPython uses wx.Accessible (MSAA-based)
- **NVDA compatibility** — Tested and used by NVDA itself
- **JAWS compatibility** — Better than Qt with proper wx.Accessible implementation

**Linux:**
- **AT-SPI2** — wxPython has basic support (less mature than Qt)
- Note: Linux is lower priority for MUD client

**macOS:**
- **NSAccessibility** — wxPython support is limited
- Note: VoiceOver support is weaker; focus on NVDA/Windows for now

### Python Libraries (wxPython Stack)
- `wxPython` (4.2.5+) — GUI framework with accessibility
- `pyttsx3` — Text-to-speech (cross-platform TTS)
- `pyautogui` — Keyboard input handling (low-level)
- `pyperclip` — Clipboard access
- `telnetlib` — Telnet protocol (built-in)
- `comtypes` (Windows) — MSAA/UI Automation API access
- `pyatspi2` (Linux) — AT-SPI2 for accessibility
- `pyobjc` (macOS) — Objective-C bridge for NSAccessibility

### Documentation & References
- [accesibilidad.md](accesibilidad.md) — Complete accessibility guidelines
- [scripts.md](scripts.md) — VipZhyla MUD reference (Reinos de Leyenda)
- [docs/mushclient_reference.md](docs/mushclient_reference.md) — MushClient accessibility research
  - Oracle system (Achaea) for blind channel management
  - Lua scripting patterns (triggers, aliases, timers)
  - Plugin architecture for accessibility
  - 500K line scrollback buffer design
- [WCAG 2.2](docs/WCAG2.2/wcag22-full.html) — Web accessibility (principles apply)
- [ChannelHistory](https://github.com/ironcross32/ChannelHistory) — Production accessibility example

---

## Current Project Status

### Phase 1 Complete (Core Infrastructure)
- **accessibility_core.py** — AccessibleControl, AccessiblePanel, AccessibleTextCtrl base classes
- **keyboard_handler.py** — KeyAction enum (24+ keybindings), KeyboardHandler with key mapping
- **audio_manager.py** — AudioLevel (5 levels: Silent→Debug), AudioManager with TTS threading
- **main.py** — VipZhylaApp and MainWindow (wxFrame single-window design)
- **tests/** — Unit tests for keyboard, audio, and core modules

### Phase 2 Priority (MUD Connection)
Next work should focus on implementing the telnet protocol layer and basic MUD parsing:
1. **src/client/connection.py** — Telnet connection management
2. **src/client/telnet_protocol.py** — Telnet protocol handling
3. **src/client/mud_parser.py** — Parse MUD output
4. **src/client/message_buffer.py** — Message history per channel
5. **Integration tests** for connection and parsing

### Reference Documentation
- **[accesibilidad.md](accesibilidad.md)** — WCAG 2.2 + accessibility patterns
- **[scripts.md](scripts.md)** — VipZhyla MUD script reference
- **[docs/mushclient_reference.md](docs/mushclient_reference.md)** — MushClient accessibility patterns (Oracle system, plugins, Lua scripting)

---

## Architecture Decisions (FINAL)

- ✅ **Framework:** wxPython 4.2.5+ (proven NVDA compatibility)
- ✅ **Accessibility:** wx.Accessible + pyttsx3 + NVDA-first testing
- ✅ **Keybindings:** WCAG 2.2-inspired with VipMud movement (Alt+U/O/I/K)
- ✅ **MUD Coverage:** Generic client, optimized for Reinos de Leyenda
- ✅ **UI Design:** Single-window + modal dialogs (Phase 2+)
- ✅ **Scripting Reference:** MushClient (Lua), Oracle (Achaea channels), VipMud (keybindings)

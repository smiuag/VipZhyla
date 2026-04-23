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

## Development Workflow

### When Starting New Feature

1. **Read accesibilidad.md** for accessibility requirements
2. **Create wxPython widget with SetName/SetDescription**
3. **Implement keyboard handler** (wxEVT_KEY_DOWN)
4. **Add TTS announcements** via audio_manager.py
5. **Test with NVDA** (Windows) before visual tweaks
6. **Document keybindings** in code and CLAUDE.md

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
- [ ] Code documented
- [ ] Tests pass (including NVDA test)

### Code Style

- Use clear, descriptive variable names
- Comment wxPython accessibility code
- Centralize keybinding definitions
- Keep UI code separate from accessibility (use accessibility_core.py)
- Prefix custom wx widgets with `Accessible` (e.g., `AccessibleTextCtrl`)

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

### Documentation
- [accesibilidad.md](accesibilidad.md) — Complete accessibility guidelines
- [scripts.md](scripts.md) — VipZhyla MUD reference
- [WCAG 2.2](docs/WCAG2.2/wcag22-full.html) — Web accessibility (principles apply)
- [ChannelHistory](https://github.com/ironcross32/ChannelHistory) — Production accessibility example

---

## Next Steps

1. ✅ **Technology Stack: wxPython (DECIDED)**
2. **Set up project structure** (src/, tests/, docs/)
3. **Implement accessibility_core.py** (wx.Accessible wrapper + TTS)
4. **Create main_window.py** (single-window wxFrame)
5. **Test with NVDA** (Windows) before adding features
6. **Iteratively add features** (connection → text display → channels → triggers)

---

## Architecture Decisions (FINAL)

- ✅ **Framework:** wxPython 4.2.5+
- ✅ **Accessibility:** wx.Accessible + pyttsx3 + NVDA focus
- ✅ **Keybindings:** New design inspired by WCAG/ChannelHistory, with VipMud movement keys (Alt+U/O/I/K for movement)
- ✅ **MUD Coverage:** Generic client, optimized for Reinos de Leyenda initially
- ✅ **UI Design:** Single-window + modal dialogs for histories

---

## Immediate TODOs (Before Phase 1)

- [ ] Create `src/` folder structure
- [ ] Set up `requirements.txt` with wxPython, pyttsx3, pyautogui
- [ ] Implement `accessibility_core.py` (wx.Accessible base class)
- [ ] Implement `keyboard_handler.py` (wxEVT_KEY_DOWN processor)
- [ ] Implement `audio_manager.py` (pyttsx3 wrapper)
- [ ] Create `main_window.py` skeleton
- [ ] Test minimal window with NVDA on Windows

# MushClient Reference - Accessibility and Architecture

A comprehensive reference for MushClient, the Windows MUD client with strong accessibility support for blind and visually impaired users.

**Repository**: [GitHub - nickgammon/mushclient](https://github.com/nickgammon/mushclient)

---

## 1. Project Overview

**MushClient** is a fast, compact Windows MUD/MUSH/MUCK/MOO client written in C++ (96.7% of codebase), maintained by Nick Gammon since 2010.

### Key Statistics
- **Language**: Primarily C++ with Lua (2.8%), VBScript, JavaScript
- **Repository**: https://github.com/nickgammon/mushclient
- **License**: Open source (check `docs/agreement.txt`)
- **Status**: Active development, 1,111+ commits
- **Community**: 203+ stars, multiple accessibility-focused forks

### Target Use Case
Originally designed for sighted MUD players, but has become **the best client option for blind players** thanks to:
- Screen reader compatibility (JAWS, NVDA, Narrator support)
- Extensive scripting system
- Community-created accessibility plugins (Oracle, etc.)

---

## 2. Core Features

### UI and Display
- **500,000 line scrollback buffer** - Extensive history
- **ANSI color support** - Full color customization
- **User-defined fonts and sizes** - Accessible typography
- **Multiple simultaneous worlds** - Open several MUDs at once
- **Miniwindows** (added 2008) - Custom graphical UI elements
- **Built-in spell checker** (Lua-based)

### Input and Automation
- **Command history** - Last 5,000 commands remembered
- **Aliases** - Custom command shortcuts
- **Triggers** - Pattern matching and auto-responses
- **Timers** - Delayed/recurring actions
- **Hotkeys** - Keyboard macros
- **Keypad navigation** - Movement shortcuts
- **Speed-walking** - Multi-step path commands
- **Auto-say** - Automatic message features

### Advanced Features
- **Logging** - Save session transcripts
- **Variables** - Store and manipulate data
- **Macro system** - Complex command sequences
- **MXP support** - MUD eXtension Protocol
- **MCCP support** - Mud Client Compression Protocol

---

## 3. Scripting System

MushClient uses a **powerful scripting architecture** that was revolutionary for MUD clients.

### Supported Languages

| Language | Native | Recommended | Notes |
|----------|--------|-------------|-------|
| **Lua** | ✅ | ⭐⭐⭐ Highly Recommended | Ships with Lua 5.1; best for cross-platform portability |
| **VBScript** | ✅ (Windows Script Host) | ⭐⭐ | Windows-only, older syntax |
| **JavaScript/JScript** | ✅ (Windows Script Host) | ⭐⭐ | Windows-only, similar to VBScript |
| **PerlScript** | ✅ | ⭐ | Requires Perl installed |
| **Python** | ✅ | ⭐ | Requires Python installed |

### Lua Integration

**Lua 5.1 Runtime:**
- Compiled into client as `lua5.1.dll`
- Module library directory for extensions (e.g., `tprint` module)
- Spell checker implemented in Lua: `spellchecker.lua`
- All documentation in built-in help system

**Key Lua Capabilities:**
```lua
-- Triggers: Match MUD output and execute actions
-- Syntax: AddTrigger(name, pattern, send_text, options)
AddTrigger("health_low", "You are in bad condition", "heal", 0)

-- Aliases: Intercept player input and transform
-- Syntax: AddAlias(name, alias_text, send_text, options)
AddAlias("gs", "getsupplies", "open bag\nget supplies from bag", 0)

-- Timers: Execute code after delay
-- Syntax: AddTimer(name, seconds, send_text, options)
AddTimer("auto_exp", 3, "experience", 0)

-- Variables: Store persistent data
SetVariable("last_kill", "orc")
victim = GetVariable("last_kill")

-- ImportXML: Dynamically create triggers/aliases at runtime
-- Syntax: ImportXML(XMLstring)
```

### Script Execution Context

Scripts can:
- **Send commands** to MUD (`Send()` function)
- **Receive output** from MUD (via triggers)
- **Manipulate variables** (local and persistent)
- **Create/modify triggers, aliases, timers** dynamically
- **Access screen reader APIs** (via plugins)
- **Write to miniwindows** (graphical UI)
- **Log and persist data** (files, variables)

### Documentation Resources

- **Official MUSHclient documentation**: https://www.gammon.com.au/scripts/doc.php
- **Lua scripting guide**: https://www.gammon.com.au/scripts/doc.php?general=lua
- **Aliases**: https://www.gammon.com.au/scripts/doc.php?general=aliases
- **Triggers**: https://www.gammon.com.au/scripts/doc.php?general=triggers
- **Features list**: https://www.gammon.com.au/scripts/doc.php?general=features
- **Forum (Gammon)**: https://www.gammon.com.au/forum

---

## 4. Accessibility for Blind/Visually Impaired Users

### Screen Reader Support

MushClient **does not have native accessibility** but works well with screen readers via a community plugin system.

#### MushReader Plugin
- **Purpose**: Automatically speaks newly arriving text
- **Screen readers supported**: JAWS, Window-Eyes, NVDA, System Access (SAPI)
- **Function**: Uses SAPI (Speech API) to announce incoming MUD text
- **Availability**: Plugin + DLL file from MushClient community

#### Known Challenges
- **UI complexity**: While using Windows standard controls, the interface requires significant scripting to be truly blind-accessible
- **Solution**: Custom Lua scripts can simplify navigation
- **No blind user has successfully written triggers without sighted assistance** (historical context)

### Community Solutions

#### Oracle System (Achaea)
**GitHub**: [achaea-oracle/oracle](https://github.com/achaea-oracle/oracle)

A comprehensive **framework for blind players in the Achaea MUD**, created by @AKJ and @RollanzMushing.

**Goals:**
- Recreate popular Mudlet scripts for MushClient
- Provide accessibility features for blind players
- Create modular framework others can extend

**Key Features:**
- Functional map system for blind navigation
- Combat spam reduction
- Channel organization (like Mudlet's ChannelHistory)
- Community-driven development (PRs welcome)

**Structure:**
- Modular Lua scripts for different features
- Sound packs for audio feedback
- Gag/filter system for message control
- Trigger/alias sets for blind-optimized gameplay

#### Blind User Community
- **Discord Server**: Available for blind/visually impaired MushClient users discussing scripts, techniques, etc.
- **Achaea Forums**: Active discussions about blind-friendly settings: https://forums.achaea.com/discussion/6658/

### Sound and Audio Integration

MushClient supports:
- **SAPI text-to-speech** (system speech engine)
- **Custom sound files** triggered by game events
- **Audio alerts** for important messages
- **Configurable verbosity** (skip low-priority announcements)

---

## 5. Technical Architecture

### Source Code Organization

```
mushclient/
├── doc/               # Documentation (help files)
├── lua/               # Lua 5.1 runtime + modules
├── locale/            # Resource DLL (en.dll) - menus, dialogs
├── scripting/         # Script engine integration
├── gui/               # Windows GUI components
├── protocol/          # MUD protocol handling (Telnet, MXP, MCCP)
├── database/          # SQLite integration
├── utils/             # Utility functions
└── [main client code] # Core C++ implementation
```

### External Dependencies

| Library | Purpose | License |
|---------|---------|---------|
| **PCRE** | Regular expressions (trigger matching) | BSD |
| **libpng** | Image handling (miniwindows) | PNG License |
| **SQLite** | Database operations (logging, storage) | Public Domain |
| **zlib** | Compression (network traffic) | Zlib |
| **Lua 5.1** | Scripting engine | MIT |

### Resource Architecture

**Separation of Concerns:**
- **en.dll** (locale directory) - Contains menus, dialogs, UI strings
- **Separate repository** (`mushclient_resources`) - Resource management
- **Advantage**: UI can be updated without recompiling core

### Compilation

- **Language**: C++ with Windows API
- **Dependencies**: External libraries (PCRE, libpng, etc.) managed via separate resources repo
- **Build System**: Standard Windows (likely Visual Studio)
- **Target**: 32/64-bit Windows executables

---

## 6. Comparison with VipZhyla/wxPython Goals

### What We Can Learn from MushClient

| Aspect | MushClient Approach | VipZhyla Approach |
|--------|-------------------|-----------------|
| **Scripting** | Lua (powerful, extensible) | Python (accessible to sighted developers) |
| **Screen Reader** | Plugin system (SAPI-based) | Native wxPython Accessibility (wx.Accessible) |
| **Trigger System** | Regex-based pattern matching | Similar approach (will implement) |
| **Accessibility** | Community-driven plugins | Built-in from day 1 |
| **Cross-Platform** | Windows-only | Windows + macOS + Linux |
| **UI Complexity** | Single window with miniwindows | Single window + modal dialogs |
| **Audio** | SAPI speech (Windows-specific) | pyttsx3 (cross-platform TTS) |

### Blind Player Needs (Identified via MushClient Experience)

From Oracle and community feedback:
1. ✅ **Trigger/alias system** - Essential for blind gameplay
2. ✅ **Channel organization** - Separate message streams
3. ✅ **Map system** - Audio-based navigation
4. ✅ **Combat spam reduction** - Configurable gags/filters
5. ✅ **Command history** - Quick access to recent commands
6. ✅ **Consistent keybindings** - Blind users need muscle memory
7. ✅ **TTS announcements** - Audio feedback for state changes
8. ✅ **Modular scripts** - Users can enable/disable features
9. ✅ **Documentation** - Extensive help accessible to screen readers
10. ✅ **Community support** - Forum/Discord for blind players

---

## 7. Design Patterns from MushClient Worth Adopting

### 1. **Plugin Architecture**
MushClient's plugin system allowed blind-accessibility plugins (like MushReader) to extend functionality without modifying core. 

**For VipZhyla:** We can create a similar system where accessibility features and game-specific scripts are modular.

### 2. **Lua Scripting**
Lua's simplicity and power made it ideal for MUD client scripting. Blind players could eventually write their own triggers/aliases.

**For VipZhyla:** Python is more accessible to sighted developers, but we should keep scripting simple and well-documented.

### 3. **Miniwindows**
MushClient's miniwindows allowed custom UI without rebuilding core.

**For VipZhyla:** Our wxPython panels can serve similar purpose—separate concerns while keeping single main window.

### 4. **Trigger/Alias/Timer System**
The trio of (pattern → action) is powerful for automation.

**For VipZhyla:** We'll implement this in `models/triggers.py`

### 5. **Variable Storage**
Persistent key-value storage for character state, settings, game data.

**For VipZhyla:** We'll use SQLite (like MushClient) for persistence.

### 6. **Scrollback Buffer + History**
500,000-line buffer allowed reviewing past events. Essential for blind users who can't skim visually.

**For VipZhyla:** We'll implement extensible history with search.

### 7. **World Management**
Multiple simultaneous MUD connections in single client.

**For VipZhyla:** Planned for Phase 3+

---

## 8. Blind User Testimonies (from MushClient Experience)

From Oracle and community discussions:

> "MushClient is the best client for blind players... but it's not really accessible without custom scripts." 
> — Blind MUD player on Achaea Forums

> "A functional map system and combat spam reduction are critical for blind gameplay."
> — Oracle creator (accessibility requirements)

> "We need consistent keybindings and clear audio feedback."
> — Blind player community feedback

### Implications for VipZhyla
- Built-in accessibility from day 1 (not a plugin)
- Clear audio feedback for all state changes
- Consistent VipMud-inspired keybindings
- Community-friendly modular design

---

## 9. Resources and References

### Official MushClient
- **Website**: https://www.mushclient.com/
- **GitHub**: [nickgammon/mushclient](https://github.com/nickgammon/mushclient)
- **Documentation**: https://www.gammon.com.au/scripts/doc.php
- **Forum**: https://www.gammon.com.au/forum

### Accessibility and Community
- **Oracle (Achaea)**: [achaea-oracle/oracle](https://github.com/achaea-oracle/oracle)
- **Achaea Forums**: https://forums.achaea.com/discussion/6747/oracle-a-mushclient-system-for-blind-players
- **Blind MUD Players Discord**: Community server (available in Achaea Forums)
- **MushClient Wiki**: https://muds.fandom.com/wiki/MUSHclient

### Related Projects
- **MUME MushClient Scripts**: [MUME/mushclient-mume](https://github.com/MUME/mushclient-mume)
- **Achaea Triggers**: [VKen/Achaea-triggers](https://github.com/VKen/Achaea-triggers)
- **MushReader Resources**: https://allinaccess.com/mc/

---

## 10. Summary: Key Takeaways for VipZhyla

### What MushClient Got Right
1. ✅ Powerful scripting system (Lua)
2. ✅ Extensive trigger/alias/timer system
3. ✅ Community-driven accessibility (Oracle)
4. ✅ Flexible single-window design
5. ✅ Multi-session support
6. ✅ Cross-MUD compatibility

### What We Can Do Better (in VipZhyla)
1. ✅ **Native accessibility** (not plugin-based)
2. ✅ **Cross-platform** (Windows + macOS + Linux)
3. ✅ **Modern TTS** (pyttsx3, not just SAPI)
4. ✅ **Keyboard-first design** (from day 1)
5. ✅ **Built-in help for blind users** (not afterthought)
6. ✅ **Python scripting** (more accessible than Lua for sighted devs)

### Implementation Roadmap (Inspired by MushClient)
- **Phase 1** ✅ Accessibility core + keyboard + TTS
- **Phase 2** Connection + basic parsing
- **Phase 3** Trigger/alias/timer system
- **Phase 4** Channel organization (like Oracle)
- **Phase 5** Scripting system (Python-based)
- **Phase 6** Community features (forums, script sharing)

---

**Last Updated**: 2026-04-23

**Document Purpose**: Reference for blind-user accessibility patterns and MUD client design lessons from MushClient.

**Next Steps for VipZhyla**: Review Oracle's implementation for channel handling and consider similar modular architecture.

# Phase 5.1: Real NVDA/JAWS Testing Checklist

**Goal:** Verify VipZhyla works end-to-end with actual screen readers on a real MUD server.

**Prerequisites:**
- [ ] NVDA 2024+ installed and ready (https://www.nvaccess.org)
- [ ] MUD server credentials and access
- [ ] VipZhyla fully built and tested (Phase 1-5 complete)

---

## Pre-Testing Setup

### Configuration
- [ ] Edit `src/config/mud_config.json` with your MUD details:
  - [ ] Set `server.host` to your MUD server (e.g., `reinos.example.com`)
  - [ ] Set `server.port` to the MUD port (e.g., `4000`)
  - [ ] Set `character.name` to your character
  - [ ] Set `character.password` to your password
  - [ ] Verify `automation.auto_load_triggers` is `true`
  - [ ] Verify `accessibility.tts_enabled` is `true`

### Verification
- [ ] Run `python test_config_loading.py` - should show all 14 checks pass
- [ ] Run `python test_keyboard_navigation.py` - should show all 24 shortcuts verified
- [ ] Run `python test_system_integration.py` - end-to-end workflow should pass

### Screen Reader Setup
- [ ] Launch NVDA: `Win + Ctrl + N`
- [ ] Verify NVDA speaks "NVDA started"
- [ ] Leave NVDA running during testing
- [ ] Disable mouse/touchpad for keyboard-only testing

---

## Application Startup Test

- [ ] Run: `python src/main.py`
- [ ] NVDA should announce "VipZhyla window"
- [ ] Listen for TTS: "Application started"
- [ ] Verify no errors in console
- [ ] Application window appears (sighted tester confirms)

---

## Connection Test

### Establishing Connection
- [ ] Press `Ctrl+K` to open connection dialog
- [ ] NVDA reads "Connect dialog opened"
- [ ] Verify dialog fields are readable:
  - [ ] NVDA reads "Server host"
  - [ ] NVDA reads "Port"
  - [ ] NVDA reads "Character name"
  - [ ] NVDA reads "Password"
- [ ] Press `Tab` to navigate through fields
- [ ] Press `Enter` to connect
- [ ] Listen for TTS: "Connecting to MUD..."

### After Connection
- [ ] NVDA announces "Connected to server"
- [ ] MUD login prompt appears in output
- [ ] Character auto-logs in (if configured)
- [ ] MUD welcome message is read by NVDA
- [ ] Verify character state displays (HP, MP, level, etc.)

---

## Basic Interaction Test

### Movement Commands
- [ ] Press `Alt+U` (west)
- [ ] NVDA reads MUD movement response
- [ ] Press `Alt+O` (east)
- [ ] Press `Alt+8` (north)
- [ ] Press `Alt+K` (south)
- [ ] Verify all directions produce MUD output
- [ ] Listen for any TTS announcements

### Command Input
- [ ] Press `Tab` until focus is in input field
- [ ] Type: `look`
- [ ] Press `Enter`
- [ ] NVDA reads room description
- [ ] Verify command was sent and response received

### History Navigation
- [ ] Press `Shift+F1` (channel history)
- [ ] NVDA announces "Channel history dialog"
- [ ] Listen for list of messages
- [ ] Press `Up/Down` arrow keys to navigate
- [ ] NVDA reads each message
- [ ] Press `Escape` to close
- [ ] Verify focus returns to main window

---

## Trigger System Test

### Create Simple Trigger
- [ ] Press `Ctrl+T` (trigger manager)
- [ ] NVDA announces "Trigger manager dialog"
- [ ] Press `Tab` to navigate
- [ ] Verify accessible labels:
  - [ ] "Name" field
  - [ ] "Pattern" field
  - [ ] "Enabled" checkbox
  - [ ] "New" button
- [ ] Click [Nuevo] button
- [ ] TriggerEditDialog opens
- [ ] Enter trigger name: "Test Health"
- [ ] Enter pattern: "health|low"
- [ ] Add action: TTS "Health warning!"
- [ ] Click [Aceptar]
- [ ] Trigger appears in list
- [ ] NVDA announces trigger in list

### Fire Trigger
- [ ] Close trigger manager (`Escape`)
- [ ] Type MUD command that matches pattern (e.g., `health`)
- [ ] Verify TTS announces: "Health warning!"
- [ ] Trigger fired correctly

### Edit Trigger
- [ ] Open trigger manager (`Ctrl+T`)
- [ ] Select trigger with arrow keys
- [ ] Click [Editar] button
- [ ] Dialog shows trigger details
- [ ] Modify trigger (e.g., change name)
- [ ] Click [Aceptar]
- [ ] Verify changes persist

---

## Advanced Features Test

### OR Conditions
- [ ] Create trigger with OR group:
  - [ ] Name: "Critical Resource"
  - [ ] Pattern: "resources|status"
  - [ ] Condition: `(hp_pct < 30) OR (mp_pct < 20)`
  - [ ] Action: TTS "Critical! Resources low!"
- [ ] Test trigger:
  - [ ] When HP drops below 30%, TTS fires
  - [ ] When MP drops below 20%, TTS fires
- [ ] Verify both conditions work independently

### Trigger Chaining
- [ ] Create trigger A:
  - [ ] Pattern: "poison|toxic"
  - [ ] Action: `EXECUTE_TRIGGER: [trigger B ID]`
- [ ] Create trigger B:
  - [ ] Name: "Antidote Alert"
  - [ ] Action: TTS "Drink antidote immediately!"
- [ ] Fire trigger A (type text matching "poison")
- [ ] Verify trigger B fires automatically
- [ ] NVDA announces chained TTS

### Storage Actions
- [ ] Create trigger:
  - [ ] Pattern: "buff|stronger"
  - [ ] Action: `STORAGE: buffs, ADD`
- [ ] Fire trigger
- [ ] Verify character state shows buff in status
- [ ] Verify no duplicate entries (spam prevention)

---

## Audio Feedback Test

### TTS Verification
- [ ] Create multiple triggers with TTS actions
- [ ] Fire each trigger
- [ ] Verify:
  - [ ] TTS is audible
  - [ ] Speech is clear (not garbled)
  - [ ] Speed is appropriate (not too fast/slow)
  - [ ] No overlapping announcements
  - [ ] Volume is balanced with MUD text

### Verbosity Levels
- [ ] Test `Ctrl+Shift+V` to toggle verbosity
- [ ] NVDA announces "Verbose mode ON" / "Verbose mode OFF"
- [ ] In verbose mode, more announcements occur
- [ ] In silent mode, only critical alerts announce

### State Announcements
- [ ] Engage in combat
- [ ] Verify TTS: "In combat"
- [ ] Cast spell or heal
- [ ] Verify TTS announces state changes
- [ ] Leave combat
- [ ] Verify TTS: "Combat ended"

---

## Accessibility Navigation Test

### Full Keyboard Navigation
- [ ] Complete entire game session using ONLY keyboard:
  - [ ] Move around world (Alt+QWERTY)
  - [ ] Open trigger manager (Ctrl+T)
  - [ ] Navigate lists with arrows
  - [ ] Open/close dialogs with Tab/Escape
  - [ ] Send commands (type + Enter)
  - [ ] Access history (Shift+F1-F4)
- [ ] Verify all actions work without mouse
- [ ] No clicks required anywhere

### Tab Order Verification
- [ ] Press `Tab` repeatedly in each window
- [ ] Verify logical order:
  - [ ] Main window: input → output → status
  - [ ] Trigger manager: list → buttons
  - [ ] Edit dialog: name → pattern → conditions → actions → buttons
- [ ] Press `Shift+Tab` to go backwards
- [ ] Verify backward navigation works correctly

### Focus Indicators
- [ ] Ask sighted tester to verify:
  - [ ] Focused element has visible outline/highlight
  - [ ] Input cursor is visible
  - [ ] Button focus is clearly indicated
  - [ ] List selection is visually distinct

### Dialog Navigation
- [ ] Open any dialog (`Ctrl+T`)
- [ ] Press `Tab` through all controls
- [ ] Verify NVDA announces:
  - [ ] Field labels
  - [ ] Input types (text box, checkbox, button)
  - [ ] Button names with keyboard shortcuts (&Nuevo)
- [ ] Press `Escape` closes dialog gracefully
- [ ] Focus returns to parent window

---

## Real-World Gameplay Test

### Basic Combat
- [ ] Engage in combat encounter
- [ ] Enemies attack
- [ ] Verify TTS announces damage
- [ ] Character health drops
- [ ] Verify HP trigger fires if configured
- [ ] Cast healing spell
- [ ] Verify healing is announced
- [ ] Combat ends
- [ ] Verify final status announced

### Loot & Items
- [ ] Defeat enemy
- [ ] Collect loot
- [ ] Verify item acquisition announced
- [ ] Check inventory
- [ ] Verify items listed accessibly

### NPC Interaction
- [ ] Talk to NPC
- [ ] Verify dialogue is readable
- [ ] Complete transaction
- [ ] Verify changes announced (inventory updated, money changed)

### Movement & Exploration
- [ ] Navigate to new area
- [ ] Verify room description is accessible
- [ ] Explore exits
- [ ] Use history to navigate (`Shift+F1`)
- [ ] Return to previous rooms
- [ ] Verify backwards navigation works

---

## Performance & Stability Test

### System Stability
- [ ] Run for 15+ minutes of continuous gameplay
- [ ] Monitor for:
  - [ ] Memory leaks (system not slowing down)
  - [ ] Frozen UI (all keyboard input responsive)
  - [ ] Lost connection (automatic reconnect?)
  - [ ] Dropped triggers (all patterns still matching)
- [ ] Verify no crashes or errors

### Trigger Latency
- [ ] Test rapid-fire triggers:
  - [ ] Take 5+ hits of damage quickly
  - [ ] Verify all damage announcements processed
  - [ ] No missed triggers
  - [ ] TTS announcements complete fully
- [ ] Test complex pattern:
  - [ ] Fire 3 triggers simultaneously
  - [ ] Verify all execute without conflicts
  - [ ] No performance degradation

### High Load
- [ ] Create 20+ complex triggers
- [ ] Engage in fast-paced combat
- [ ] Verify system handles load:
  - [ ] No freezing or lag
  - [ ] Triggers still fire correctly
  - [ ] TTS announcements complete
  - [ ] No missed game messages

---

## Edge Cases & Error Handling

### Connection Errors
- [ ] Disconnect network temporarily
- [ ] Verify TTS announces: "Connection lost"
- [ ] Reconnect network
- [ ] Verify auto-reconnect works (if enabled)
- [ ] Game state resumes correctly

### Invalid Patterns
- [ ] Create trigger with invalid regex
- [ ] Test if error is announced
- [ ] Verify error message is clear
- [ ] Fix trigger
- [ ] Verify it works

### Disabled Triggers
- [ ] Disable a trigger (toggle enabled checkbox)
- [ ] Fire the trigger
- [ ] Verify it does NOT fire
- [ ] Re-enable trigger
- [ ] Fire again
- [ ] Verify it DOES fire

### Large Output
- [ ] Generate large MUD output (combat with many creatures)
- [ ] Verify system keeps up:
  - [ ] All lines processed
  - [ ] No dropped messages
  - [ ] History still accessible
  - [ ] Scrollback works smoothly

---

## Comparative Testing (If Multiple Readers Available)

### NVDA vs JAWS (if available)
- [ ] Repeat critical tests with JAWS
- [ ] Verify:
  - [ ] Same accessibility
  - [ ] Different verbosity levels work
  - [ ] Both readers speak TTS correctly
  - [ ] Both support all keyboard shortcuts

### NVDA vs Narrator (Windows built-in)
- [ ] Enable Narrator: `Win + Ctrl + Enter`
- [ ] Repeat basic tests
- [ ] Verify Narrator also reads everything
- [ ] Note any differences in speech quality

---

## Final Verification Checklist

- [ ] **Connectivity:** MUD connects and stays connected
- [ ] **Accessibility:** 100% keyboard navigation, no mouse needed
- [ ] **Audio:** TTS announcements clear and timed correctly
- [ ] **Triggers:** All trigger types work (simple, OR, NOT, chaining)
- [ ] **Performance:** System stable under load for 15+ minutes
- [ ] **Stability:** No crashes, memory leaks, or errors
- [ ] **Completeness:** All Phase 1-5 features working together

---

## Issues Found

If you find problems, document them here with:
- **Issue:** What went wrong
- **Steps:** How to reproduce
- **Expected:** What should happen
- **Actual:** What actually happened
- **Reader:** NVDA/JAWS/Narrator
- **OS:** Windows version
- **Impact:** Critical/High/Medium/Low

---

## Test Report

**Date:** ___________

**Tester:** ___________

**System:** ___________

**Screen Readers Tested:**
- [ ] NVDA 2024.x
- [ ] JAWS 2024.x
- [ ] Narrator

**Overall Result:** ✓ PASS / ✗ FAIL

**Issues Found:** _________ (number)

**Critical Issues:** _________ (blockers for release)

**Notes:**

```
(Add any observations, unusual behaviors, or successes here)
```

---

## Sign-Off

- [ ] All core features working
- [ ] Accessibility verified
- [ ] Performance acceptable
- [ ] Ready for user testing

**Approved for public release:** YES / NO

---

## Next Steps After Phase 5.1

1. **If PASS:** Continue to Phase 6 (Advanced Features)
   - Map system
   - Scripting system
   - Extended aliases
   - Macro system

2. **If FAIL:** Fix critical issues, re-test

3. **Optional:** Performance profiling and optimization (Phase 5.2)

---

**End of Phase 5.1 Checklist**

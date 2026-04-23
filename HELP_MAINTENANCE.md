# Help System Maintenance Guide

**IMPORTANT:** When you add, change, or remove features, you MUST update the help system to match.

The help system is the user's primary source of documentation. It must always be accurate and complete.

## Where Help Lives

**User-facing help:** `src/ui/help_dialog.py`
- Contains `HelpDialog.HELP_CONTENT` dictionary with 8 tabs of help text
- Displayed when user presses **F1**
- Fully accessible: multiline text, keyboard-navigable tabs

**This file:** `HELP_MAINTENANCE.md`
- Instructions for keeping help synchronized

## Help Tabs

| Tab | Content | Update When |
|-----|---------|------------|
| Start Here | Overview, quick start | Product changes |
| Connection | Connect/disconnect, server info | Connection behavior changes |
| Movement | All movement keybindings (Alt+U/O/I/K/etc) | Movement commands change |
| Messages | Message history (Shift+F1-F4), navigation | Message dialogs change |
| Typing | Sending commands, aliases mention | Command system changes |
| Triggers | Trigger system explanation, usage | Trigger logic changes |
| Aliases | Alias system explanation, usage | Alias system changes |
| Timers | Timer system explanation, usage | Timer system changes |
| Settings | Audio, verbosity, status bar | Settings/UI changes |
| Keyboard Map | Complete list of all keybindings | Any keybinding changes |

## Synchronization Rules

### Rule 1: Add Feature → Update Help
When adding a new feature:
1. Implement the feature
2. Create or update the relevant help tab
3. Add the keybinding to the "Keyboard Map" tab
4. Test that F1 opens help and shows the new content

Example: Added Ctrl+T for triggers?
```python
# In src/ui/help_dialog.py
"Triggers": (
    "TRIGGERS - REACT TO EVENTS\n"
    "...\n"
    "  Press Ctrl+T to open Trigger Manager\n"
    "...\n"
),

# In "Keyboard Map" tab
"MANAGEMENT:\n"
"  Ctrl+T = Triggers/Aliases/Timers\n"
```

### Rule 2: Change Keybinding → Update Help
When you change a keybinding (e.g., F1 → F2):
1. Update `keyboard_handler.py` (the keybinding definition)
2. Update the help text in TWO places:
   - The relevant tab (e.g., "Triggers" tab if changing Ctrl+T)
   - The "Keyboard Map" tab (the complete reference)

Example: Changed movement key from Alt+U to Alt+W?
```python
# In src/ui/help_dialog.py, "Movement" tab
"  Alt+W = West  (was Alt+U)"

# In "Keyboard Map" tab
"MOVEMENT (Alt+Key):\n"
"  W=West, O=East, ..."
```

### Rule 3: Remove Feature → Update Help
When removing a feature:
1. Remove the keybinding from `keyboard_handler.py`
2. Remove or update the help tab
3. Remove from "Keyboard Map" tab

Example: Removing verbosity toggle?
```python
# Delete or empty the tab
"Settings": (
    "AUDIO\n"
    "=====\n"
    "..."
    # Remove the Verbosity section
)

# Remove from Keyboard Map
"MANAGEMENT:\n"
"  Ctrl+T = Triggers/Aliases/Timers\n"
# (Remove "Ctrl+Shift+V = Toggle Verbose")
```

### Rule 4: Fix Keybinding in Help
When help text has wrong keybindings:
1. Update both the specific tab AND "Keyboard Map"
2. Search help_dialog.py for ALL occurrences of that keybinding
3. Verify the change is correct in `keyboard_handler.py`

## Checklist: Adding a New Feature

```
[ ] Feature implemented
[ ] Keybinding defined in keyboard_handler.py
[ ] Handler registered in main.py
[ ] Help content written in help_dialog.py
  [ ] Specific tab updated (e.g., "Triggers")
  [ ] "Keyboard Map" tab updated
[ ] F1 opens help and shows new content
[ ] Tested with screen reader (if applicable)
[ ] Help is non-technical and user-friendly
```

## Checklist: Changing a Keybinding

```
[ ] Keybinding updated in keyboard_handler.py
[ ] Handler updated in main.py (if needed)
[ ] Help specific tab updated (e.g., "Triggers")
[ ] "Keyboard Map" tab updated
[ ] All references to old keybinding removed
[ ] F1 opens help and shows correct keybinding
[ ] Tested in application
```

## Help Writing Style

**Be user-friendly:**
- ❌ "Register a trigger using TriggerManager.add_trigger()"
- ✓ "Press Ctrl+T to open Trigger Manager"

**Include examples:**
- ❌ "You can create shortcuts"
- ✓ "Type 'h' and press Enter, it sends 'help'"

**Explain why, not just how:**
- ❌ "Timers execute actions at intervals"
- ✓ "Timers let you do something automatically every N seconds. Examples: check health, announce to group, remind yourself of a task"

**Use consistent formatting:**
- Section headers: `TOPIC NAME` in caps
- Subsections: standard capitalization
- Keyboard keys: `Ctrl+K`, `Alt+U`, `F1`
- Game commands: in monospace (`help`, `look`, `examine potion`)

## Testing Help

```bash
# Manual test:
python src/main.py
# Press F1
# Verify:
#   - Dialog opens
#   - All 10 tabs visible
#   - Content readable
#   - Screen reader announces tabs
#   - Arrow keys navigate tabs
#   - Text wraps properly
#   - Escape or Close closes dialog
```

## Synchronization Examples

### Example 1: Added new movement command (Alt+N for north)
```python
# keyboard_handler.py - KeyAction enum
MOVE_NORTH = "move_north"  # Alt+N (was Alt+8)

# main.py - register handler
self.keyboard.register_handler(KeyAction.MOVE_NORTH, lambda e: self.send_command("north"))

# help_dialog.py - "Movement" tab AND "Keyboard Map" tab
"Movement": (
    "MOVING AROUND\n"
    "=============\n\n"
    "Use Alt+Key to move:\n"
    "  Alt+U = West\n"
    "  Alt+O = East\n"
    "  Alt+N = North  (was Alt+8)\n"  ← Updated
    ...
)

"Keyboard Map": (
    "MOVEMENT (Alt+Key):\n"
    "  U=West, O=East, N=North, ...  ← Updated
    ...
)
```

### Example 2: Added new feature (macro recording)
```python
# keyboard_handler.py - KeyAction enum
RECORD_MACRO = "record_macro"  # Ctrl+R

# keyboard_handler.py - _build_key_map()
key_map[(ord('R'), wx.MOD_CONTROL)] = KeyAction.RECORD_MACRO

# help_dialog.py - Add new tab or add to existing tab
"Macros": (
    "MACROS - RECORD & REPLAY\n"
    "========================\n\n"
    "Record a series of commands and replay them with one keypress.\n\n"
    "To record:\n"
    "  Press Ctrl+R\n"
    "  Type your commands normally\n"
    "  Press Ctrl+R again to stop\n\n"
    "To replay:\n"
    "  Press Ctrl+M\n\n"
    ...
)

# help_dialog.py - Update "Keyboard Map"
"Keyboard Map": (
    "...\n"
    "MANAGEMENT:\n"
    "  Ctrl+T = Triggers/Aliases/Timers\n"
    "  Ctrl+R = Record Macro\n"  ← Added
    "  Ctrl+M = Play Macro\n"    ← Added
    "  ...\n"
)
```

## Questions?

If you're not sure whether help needs updating:
1. Ask: "Would a user need to know about this?"
2. If yes → update help
3. If it changes behavior → update help
4. When in doubt → update help

Keep help current. A user relying on outdated help will get frustrated and think the app is broken.

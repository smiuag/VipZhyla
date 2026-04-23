# Phase 2.5 Complete — History Dialogs (Shift+F1-F4)

## Summary

Implemented accessible modal dialogs for reviewing message history by channel, with full keyboard navigation and screen reader support.

## Changes

### New File: `src/ui/list_dialogs.py` (381 lines)

**HistoryDialog (base class)**
- Modal dialog for reviewing a single channel's message history
- `wx.ListBox` with message list (accessible to screen readers natively)
- Messages formatted as "HH:MM  text" with timestamp
- Keyboard navigation: Up/Down (prev/next), PgUp/PgDn (jump 10), Home/End (first/last)
- Escape closes dialog
- TTS announces position on each selection: "Mensaje N de Total"
- Status label shows "N / Total" for sighted users

**ChannelHistoryDialog (extended class)**
- Multi-channel switcher for communication channels
- Shows BANDO, TELEPATHY, CITIZENSHIP, GROUP
- Starts on BANDO if available, else first channel with messages
- Alt+Left/Right switches between channels
- Same navigation + TTS as base class
- On channel switch: announces "Bando: 42 mensajes"

**Factory Functions**
- `show_channel_history()` — Shift+F1: All comm channels with switcher
- `show_room_history()` — Shift+F2: GENERAL channel only
- `show_telepathy_history()` — Shift+F3: TELEPATHY channel only
- `show_event_list()` — Shift+F4: SYSTEM channel only

### Modified: `src/main.py`

**Imports**
```python
from ui.list_dialogs import (show_channel_history, show_room_history,
                             show_telepathy_history, show_event_list)
```

**New Keyboard Handlers** (6 total)
- Shift+F1 → `on_show_channel_history()`
- Shift+F2 → `on_show_room_history()`
- Shift+F3 → `on_show_telepathy_history()`
- Shift+F4 → `on_show_event_list()`
- Alt+Left → `on_prev_channel()` (cycle through channels with messages)
- Alt+Right → `on_next_channel()` (cycle through channels with messages)

**New Methods**
- `on_show_channel_history()` — Opens ChannelHistoryDialog
- `on_show_room_history()` — Opens HistoryDialog for GENERAL
- `on_show_telepathy_history()` — Opens HistoryDialog for TELEPATHY
- `on_show_event_list()` — Opens HistoryDialog for SYSTEM
- `on_prev_channel()` — Cycles to previous channel, announces name + count
- `on_next_channel()` — Cycles to next channel, announces name + count

### New File: `tests/test_list_dialogs.py` (143 lines)

Tests for data layer logic (message formatting, channel filtering, position info):
- `test_channel_list_filtering()` — Verify channels with messages are retrievable
- `test_comm_channel_filtering()` — Verify communication channels filter correctly
- `test_position_info_for_display()` — Position info updates correctly as user navigates
- `test_empty_channel_handling()` — Empty channels handled gracefully
- `test_all_channels_list()` — Non-empty channels listed correctly

## Accessibility Features

✓ **Screen Reader Compatible**
- `wx.ListBox` reads items automatically on arrow navigation (NVDA native support)
- Dialog title announced on open
- Message text read automatically as user navigates

✓ **Keyboard-Only**
- All navigation via keyboard
- No mouse required
- Escape closes dialog
- Up/Down for message navigation
- Alt+Left/Right for channel switching (in ChannelHistoryDialog)

✓ **Audio Feedback (TTS)**
- "Mensaje N de Total" on every message selection
- "Bando: 42 mensajes" on channel switch
- Verbosity levels respected (SILENT/MINIMAL/NORMAL/VERBOSE/DEBUG)

✓ **Visual Feedback**
- Status label shows "N / Total" for sighted users
- Channel label shows current channel (ChannelHistoryDialog)
- Message list scroll position visible

## Testing

Data layer tests pass (message buffer integration):
```bash
pytest tests/test_list_dialogs.py -v
```

Full UI testing requires wxPython display environment and can be done manually:
```bash
python src/main.py
# Shift+F1 opens channel history dialog
# Alt+Left/Right in dialog switch channels
# Escape closes dialog
```

## Performance

- No performance impact on main window
- Dialogs load channel data from MessageBuffer (RLock-protected, thread-safe)
- Max 5000 messages per channel (configurable via `MessageBuffer.MAX_MESSAGES_PER_CHANNEL`)
- Dialog window size: 600x400 (resizable)

## Next Steps

### Phase 3: Trigger/Alias/Timer System
- Implement `src/models/triggers.py` with pattern matching
- Support for aliases (command substitution)
- Support for triggers (pattern → action)
- Support for timers (periodic actions)

### Phase 4: Advanced Features
- Map system (track location, show exits)
- Combat assistance (health tracking, ability triggers)
- Experience/level tracking
- Status line enhancements

### Phase 5: Polish & Testing
- Integration test with real NVDA
- Integration test with JAWS
- Integration test with Narrator
- Performance testing with large message buffers
- Documentation updates

## Known Limitations

- macOS VoiceOver support incomplete (wxPython limitation)
- Dialog navigation within list only; no cross-dialog navigation yet
- Channel switching in main window (Alt+Left/Right) announces but doesn't change displayed channel

## Code Quality

- All syntax verified with `python -m py_compile`
- No new dependencies added
- Follows existing patterns: relative imports, callback architecture, TTS integration
- Comments only for non-obvious logic (ChannelHistoryDialog channel cycling)

## Commit Hash

```
b7aec32 Phase 2.5: Implement history dialogs (Shift+F1-F4) with accessible UI
```

# Testing VipZhyla with Screen Readers

Guide for testing VipZhyla with NVDA, JAWS, or Windows Narrator to verify accessibility features.

## Prerequisites

### For NVDA (Free)
- Download: https://www.nvaccess.org/download/
- Install and launch: `nvda.exe`
- Or enable with: `Win + Ctrl + N`

### For Windows Narrator (Built-in)
- Enable with: `Win + Ctrl + Enter`
- Disable with: `Win + Ctrl + Enter`

### For JAWS (Commercial)
- Requires JAWS 2024 or later
- Launch Freedom Scientific JAWS
- Or enable with: `Insert + Alt + N`

## Quick Start: Testing with Simulator

The MUD Simulator allows testing without a live MUD connection.

### 1. Enable Your Screen Reader
```bash
# NVDA
Win + Ctrl + N

# Narrator
Win + Ctrl + Enter

# JAWS (already running)
```

### 2. Run the Integration Test
```bash
cd C:\proyectos\Claude\VipZhyla
python test_simulator_integration.py
```

### 3. Listen For:
- **MUD Output**: Screen reader reads each line of MUD text
- **Trigger TTS**: "Health warning: HP below 50 percent"
- **Buff Announcement**: "Buff received!"
- **Status Updates**: "HP 340/500"

## Test Scenarios

The `MUDSimulator` provides 10 different scenarios:

```bash
# List all scenarios
python -c "from src.client.mud_simulator import MUDSimulator; s = MUDSimulator(); s.list_scenarios()"

# Run specific scenario
python -c "
from src.client.mud_simulator import MUDSimulator
s = MUDSimulator()
s.set_output_callback(lambda x: print(f'[MUD] {x}'))
s.run_scenario('boss')  # boss, combat, poison, quest, rapid, etc.
"
```

### Available Scenarios

| Scenario | Key | What to Listen For |
|----------|-----|-------------------|
| Basic Combat | `combat` | Damage, low health warning, healing |
| Poison & Cure | `poison` | Poisoned alert, poison removal |
| Level Up | `levelup` | New level announcement, ability gain |
| Multi-Enemy | `multi` | Multiple damage sources, quick reactions |
| Boss Fight | `boss` | High-impact events, legendary status |
| Exploration | `explore` | Discovery alerts, item acquisition |
| Conversation | `talk` | NPC dialogue, transaction confirmations |
| Status | `status` | Periodic status updates, level up |
| Quest | `quest` | Quest objectives, rewards |
| Rapid Combat | `rapid` | Fast-paced triggers (tests latency) |

## Testing Checklist

### Screen Reader Integration
- [ ] NVDA reads MUD output lines
- [ ] JAWS announces trigger TTS messages
- [ ] Narrator speaks character state changes
- [ ] No garbled or repeated speech

### Keyboard Navigation
- [ ] Tab cycles through UI elements
- [ ] Alt+F12 opens Settings
- [ ] Shift+F1-F4 opens history dialogs
- [ ] Enter/Space activates buttons

### Trigger System
- [ ] TTS announcements are clear and timely
- [ ] Sound effects play at appropriate volume
- [ ] Character state updates are logged
- [ ] Rapid-fire triggers don't overwhelm

### Edge Cases
- [ ] Long trigger announcements complete fully
- [ ] Multiple simultaneous triggers handled
- [ ] Screen reader can interrupt/skip if needed
- [ ] Status changes are detectable

## Real MUD Testing

Once the simulator is working, test with a real MUD:

### 1. Configure MUD Connection
Edit `src/config/mud_config.json`:
```json
{
  "host": "your.mud.server",
  "port": 4000,
  "character": "YourCharacter",
  "password": "your_password"
}
```

### 2. Launch Application
```bash
python src/main.py
```

### 3. Enable Screen Reader
- Enable NVDA/JAWS/Narrator
- Connect to MUD
- Test keyboard navigation and TTS

### 4. Test Real Scenarios
- [ ] Combat encounter
- [ ] Receiving buffs/debuffs
- [ ] Level up notifications
- [ ] Character status changes
- [ ] Trigger firing on game events

## Common Issues & Solutions

### Issue: Screen Reader Doesn't Read TTS
**Solution:**
- Verify TTS engine is configured (pyttsx3)
- Check audio output device
- Run: `python test_startup.py` to verify audio

### Issue: Triggers Not Firing
**Solution:**
- Check pattern matching: `python test_triggers_conditions.py`
- Verify character state: `python test_advanced_conditions.py`
- Test with simulator: `python test_simulator_integration.py`

### Issue: Rapid Fire Triggers Overwhelming
**Solution:**
- Reduce number of simultaneous triggers
- Increase TTS delay between announcements
- Test "rapid" scenario to identify latency

### Issue: NVDA/JAWS Not Detecting Input
**Solution:**
- Verify wxPython accessibility: `python test_startup.py`
- Check NVDA/JAWS focus mode (should be in browse mode for text)
- Restart screen reader and try again

## Performance Testing

### Measure Trigger Latency
```bash
python test_edge_cases.py
```

Expected results:
- Individual trigger: < 100ms
- Chain (A->B->C): < 300ms
- Rapid fire (10+ triggers): < 500ms

### Stress Test
```bash
python -c "
from src.client.mud_simulator import MUDSimulator
s = MUDSimulator()
s.set_output_callback(print)
s.run_scenario('rapid')
"
```

Listen for:
- All announcements complete
- No missed triggers
- Clear speech (not garbled)

## Accessibility Verification Checklist

Use this before public release:

### WCAG 2.2 AA Compliance
- [ ] All text is readable by screen readers
- [ ] Color is not the only way to convey information
- [ ] Keyboard accessible without mouse
- [ ] Focus indicators are visible
- [ ] Timing not required for any function

### VipZhyla Specific
- [ ] TTS announces all important game events
- [ ] Keyboard shortcuts documented in help
- [ ] Character state accessible via keyboard
- [ ] Trigger testing available without MUD
- [ ] Error messages are clear and actionable

## Screen Reader Configuration Tips

### NVDA Best Practices
- Enable "Report focused applications": Preferences → Advanced → Report focused applications
- Use "Focus mode" (Shift+Num+Space) for interactive areas
- Enable "Speak command line": Preferences → Advanced

### JAWS Best Practices
- Enable "Verbosity Level 2" for detailed speech
- Configure "Hot Keys" for quick access
- Use "Quick Settings" (Insert+Q) for common adjustments

### Narrator Best Practices
- Enable "Verbosity Level 2" in Settings
- Use "Scan Mode" for reading continuous text
- Keyboard: Windows logo key + Alt + N for settings

## Reporting Accessibility Issues

If you find problems:

1. **Reproduce the issue**
   - Note the scenario/MUD output
   - Record screen reader behavior
   - Document keyboard/mouse actions

2. **Create GitHub Issue**
   - Title: "[ACCESSIBILITY] Brief description"
   - Include: Scenario, screen reader, OS version
   - Attach: Test output if possible

3. **Suggested Format**
   ```
   Screen Reader: NVDA 2024.4
   OS: Windows 11 Home
   Issue: TTS announcement cut off at "Health warning"
   Expected: Full phrase should complete
   Scenario: test_simulator_integration.py
   ```

## References

- **WCAG 2.2**: https://www.w3.org/WAI/WCAG22/quickref/
- **wxPython Accessibility**: https://docs.wxpython.org/accessibility.html
- **NVDA Documentation**: https://www.nvaccess.org/documentation/
- **JAWS Documentation**: https://training.freedomscientific.com/
- **pyttsx3 (TTS)**: https://pyttsx3.readthedocs.io/

## Next Steps

1. Test with each screen reader (NVDA → JAWS → Narrator)
2. Document any differences
3. Report issues with full context
4. Iterate on improvements
5. Create automated accessibility tests

---

**Goal**: VipZhyla should be fully usable with screen readers, no mouse required, with clear audio feedback for all game events.

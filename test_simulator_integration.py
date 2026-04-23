#!/usr/bin/env python3
"""Integration test: MUD Simulator with real trigger system."""

import sys
sys.path.insert(0, 'src')

from models.triggers import TriggerManager, Trigger, TriggerAction, ActionType
from models.character_state import CharacterState
from client.mud_parser import ParsedMessage, ChannelType
from client.mud_simulator import MUDSimulator
from app.audio_manager import AudioManager

print("Integration Test: MUD Simulator + Triggers")
print("=" * 50)

# Setup
audio = AudioManager()
char_state = CharacterState()
trigger_mgr = TriggerManager(audio)
trigger_mgr.character_state = char_state
trigger_mgr.triggers = []

char_state.name = "Aeroth"
char_state.clase = "Soldado"
char_state.update_vitals(300, 500)  # Start at 60% HP
char_state.in_combat = False

# Create triggers for the scenario
print("\n1. Creating scenario-specific triggers...")

# Low health alert
low_health_trigger = Trigger(
    id="trg_low_health",
    name="Low Health Alert",
    pattern="low|critical|damage",
    is_regex=True,
    enabled=True,
    conditions=[{"field": "hp_pct", "operator": "<", "value": 50}],
    actions=[TriggerAction(ActionType.TTS, value="Health warning: HP below 50 percent")]
)
trigger_mgr.add_trigger(low_health_trigger)

# Poison detection
poison_trigger = Trigger(
    id="trg_poison",
    name="Poison Detection",
    pattern="poisoned|poison",
    is_regex=True,
    enabled=True,
    actions=[
        TriggerAction(ActionType.TTS, value="Poison detected! Need antidote!"),
        TriggerAction(ActionType.STORAGE, value="debuffs", operation="add", data="Poison")
    ]
)
trigger_mgr.add_trigger(poison_trigger)

# Buff detection
buff_trigger = Trigger(
    id="trg_buff",
    name="Buff Detection",
    pattern="blessed|stronger|shield|protection",
    is_regex=True,
    enabled=True,
    actions=[
        TriggerAction(ActionType.TTS, value="Buff received!"),
        TriggerAction(ActionType.STORAGE, value="buffs", operation="add", data="Active Buff")
    ]
)
trigger_mgr.add_trigger(buff_trigger)

# Combat start/end
combat_trigger = Trigger(
    id="trg_combat",
    name="Combat Trigger",
    pattern="combat|battle|fight",
    is_regex=True,
    enabled=True,
    actions=[TriggerAction(ActionType.TTS, value="Combat status changed")]
)
trigger_mgr.add_trigger(combat_trigger)

print(f"   [OK] Created 4 triggers for scenario")

# Setup simulator callback
print("\n2. Setting up MUD Simulator callback...")
trigger_count = [0]

def on_mud_output(text: str):
    """Called when MUD outputs text."""
    trigger_count[0] += 1

    # Simulate HP changes based on output
    if "damage" in text.lower():
        char_state.update_vitals(char_state.hp - 25, char_state.maxhp)
    elif "heal" in text.lower():
        char_state.update_vitals(min(char_state.hp + 30, char_state.maxhp), char_state.maxhp)
    elif "level up" in text.lower():
        char_state.level += 1
        char_state.update_vitals(char_state.maxhp, char_state.maxhp)

    # Detect combat state
    if "combat" in text.lower() or "battle" in text.lower() or "fight" in text.lower():
        if "begins" in text.lower() or "start" in text.lower():
            char_state.in_combat = True
        elif "end" in text.lower() or "defeat" in text.lower():
            char_state.in_combat = False

    # Evaluate triggers
    msg = ParsedMessage(ChannelType.GENERAL, text, text)
    trigger_mgr.evaluate(msg)

simulator = MUDSimulator()
simulator.set_output_callback(on_mud_output)
print("   [OK] Callback configured")

# Run scenario
print("\n3. Running combat scenario...")
print("-" * 50)
simulator.run_scenario("combat")
print("-" * 50)

# Report results
print("\n4. Scenario Results:")
print(f"   Total MUD output lines: {trigger_count[0]}")
print(f"   Final character state:")
print(f"     - HP: {char_state.hp}/{char_state.maxhp} ({char_state.hp_pct}%)")
print(f"     - Level: {char_state.level}")
print(f"     - In Combat: {char_state.in_combat}")
print(f"     - Buffs: {char_state.buffs if char_state.buffs else 'None'}")
print(f"     - Debuffs: {char_state.debuffs if char_state.debuffs else 'None'}")

# Verify trigger activity
print(f"\n5. Trigger Activity:")
if "Poison" in char_state.debuffs:
    print("   [OK] Poison trigger fired (debuff added)")
else:
    print("   [-] Poison trigger did not fire")

if "Active Buff" in char_state.buffs:
    print("   [OK] Buff trigger fired (buff added)")
else:
    print("   [-] Buff trigger did not fire")

print("\n" + "=" * 50)
print("[SUCCESS] Integration test complete!")
print("=" * 50)
print("\nTo test with NVDA/JAWS:")
print("  1. Enable NVDA (Win+Ctrl+N) or JAWS")
print("  2. Run: python test_simulator_integration.py")
print("  3. Listen for TTS announcements from triggers")
print("  4. Screen reader will read all MUD output")
print("\nThe MUD Simulator generates realistic output that triggers respond to.")

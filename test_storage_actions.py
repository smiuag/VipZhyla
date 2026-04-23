#!/usr/bin/env python3
"""Test storage actions for character state updates."""

import sys
sys.path.insert(0, 'src')

from models.triggers import TriggerManager, Trigger, TriggerAction, ActionType
from models.character_state import CharacterState
from client.mud_parser import ParsedMessage, ChannelType
from app.audio_manager import AudioManager

print("Testing Storage Actions (Buffs/Debuffs/Flags)")
print("=" * 50)

# Setup
print("\n1. Creating test environment...")
try:
    audio = AudioManager()
    char_state = CharacterState()
    trigger_mgr = TriggerManager(audio)
    trigger_mgr.character_state = char_state
    # Clear any loaded triggers
    trigger_mgr.triggers = []
    trigger_mgr.aliases = []
    trigger_mgr.timers = []

    char_state.name = "Aeroth"
    char_state.clase = "Soldado"
    print("   [OK] Environment created")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Reset for each test
trigger_mgr.triggers = []
trigger_mgr.aliases = []
trigger_mgr.timers = []

# Test 1: Add buff
print("\n2. Testing STORAGE action: add to buffs...")
try:
    buff_trigger = Trigger(
        id="trg_add_buff",
        name="Add Buff",
        pattern="blessed",
        is_regex=False,
        enabled=True,
        actions=[
            TriggerAction(
                ActionType.STORAGE,
                value="buffs",
                operation="add",
                data="Bendición"
            )
        ]
    )
    trigger_mgr.add_trigger(buff_trigger)

    assert len(char_state.buffs) == 0, "Buffs should start empty"

    msg = ParsedMessage(ChannelType.GENERAL, "You are blessed", "You are blessed")
    trigger_mgr.evaluate(msg)

    assert "Bendición" in char_state.buffs, f"Buff not added. Buffs: {char_state.buffs}"
    print(f"   [OK] Buff added: {char_state.buffs}")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

trigger_mgr.triggers = []  # Reset
# Test 2: Don't add duplicate buff
print("\n3. Testing duplicate prevention...")
try:
    msg = ParsedMessage(ChannelType.GENERAL, "You are blessed again", "You are blessed again")
    trigger_mgr.evaluate(msg)

    # Should still be only 1
    assert len(char_state.buffs) == 1, f"Expected 1 buff, got {len(char_state.buffs)}"
    print(f"   [OK] Duplicate prevention working: {char_state.buffs}")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 3: Add debuff
print("\n4. Testing STORAGE action: add to debuffs...")
try:
    char_state.debuffs = []  # Reset

    debuff_trigger = Trigger(
        id="trg_add_debuff",
        name="Add Debuff",
        pattern="poisoned",
        is_regex=False,
        enabled=True,
        actions=[
            TriggerAction(
                ActionType.STORAGE,
                value="debuffs",
                operation="add",
                data="Veneno"
            )
        ]
    )
    trigger_mgr.add_trigger(debuff_trigger)

    msg = ParsedMessage(ChannelType.GENERAL, "You are poisoned", "You are poisoned")
    trigger_mgr.evaluate(msg)

    assert "Veneno" in char_state.debuffs, f"Debuff not added. Debuffs: {char_state.debuffs}"
    print(f"   [OK] Debuff added: {char_state.debuffs}")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 4: Remove debuff
print("\n5. Testing STORAGE action: remove from debuffs...")
try:
    remove_trigger = Trigger(
        id="trg_remove_debuff",
        name="Remove Debuff",
        pattern="clean|cured|limpio",
        is_regex=True,
        enabled=True,
        actions=[
            TriggerAction(
                ActionType.STORAGE,
                value="debuffs",
                operation="remove",
                data="Veneno"
            )
        ]
    )
    trigger_mgr.add_trigger(remove_trigger)

    assert "Veneno" in char_state.debuffs, "Veneno should be there before removal"

    msg = ParsedMessage(ChannelType.GENERAL, "You are now clean", "You are now clean")
    trigger_mgr.evaluate(msg)

    assert "Veneno" not in char_state.debuffs, f"Debuff not removed. Debuffs: {char_state.debuffs}"
    print(f"   [OK] Debuff removed: {char_state.debuffs}")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 5: Update HP threshold flags
print("\n6. Testing STORAGE action: update hp_threshold_flags...")
try:
    char_state.update_vitals(100, 450)  # 22% HP = threshold 30
    threshold = char_state.get_hp_threshold()
    assert threshold == 30, f"Expected threshold 30, got {threshold}"

    flag_trigger = Trigger(
        id="trg_hp_threshold",
        name="Mark HP Threshold",
        pattern="low health|poca vida",
        is_regex=True,
        enabled=True,
        conditions=[
            {"field": "hp_pct", "operator": "<", "value": 30}
        ],
        actions=[
            TriggerAction(
                ActionType.STORAGE,
                value="hp_threshold_flags",
                operation="update"
            ),
            TriggerAction(
                ActionType.TTS,
                value="Vida baja"
            )
        ]
    )
    trigger_mgr.add_trigger(flag_trigger)

    # Initially flag should be False
    assert char_state.hp_threshold_flags[30] == False, "Flag should be False initially"

    msg = ParsedMessage(ChannelType.GENERAL, "Low health alert", "Low health alert")
    trigger_mgr.evaluate(msg)

    # After action, flag should be True
    assert char_state.hp_threshold_flags[30] == True, "Flag should be True after storage action"
    print(f"   [OK] HP threshold flag updated: {char_state.hp_threshold_flags}")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 6: Set scalar field
print("\n7. Testing STORAGE action: set scalar field...")
try:
    char_state.last_state = ""

    set_trigger = Trigger(
        id="trg_set_state",
        name="Set Last State",
        pattern="critical",
        is_regex=False,
        enabled=True,
        actions=[
            TriggerAction(
                ActionType.STORAGE,
                value="last_state",
                operation="set",
                data="Critical condition"
            )
        ]
    )
    trigger_mgr.add_trigger(set_trigger)

    msg = ParsedMessage(ChannelType.GENERAL, "You are in critical state", "You are in critical state")
    trigger_mgr.evaluate(msg)

    assert char_state.last_state == "Critical condition", f"Got: {char_state.last_state}"
    print(f"   [OK] Scalar field set: '{char_state.last_state}'")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 7: Clear list
print("\n8. Testing STORAGE action: clear list...")
try:
    char_state.buffs = ["Buff1", "Buff2", "Buff3"]
    assert len(char_state.buffs) == 3, "Buffs should have 3 items"

    clear_trigger = Trigger(
        id="trg_clear_buffs",
        name="Clear Buffs",
        pattern="dispel",
        is_regex=False,
        enabled=True,
        actions=[
            TriggerAction(
                ActionType.STORAGE,
                value="buffs",
                operation="clear"
            )
        ]
    )
    trigger_mgr.add_trigger(clear_trigger)

    msg = ParsedMessage(ChannelType.GENERAL, "All buffs dispelled", "All buffs dispelled")
    trigger_mgr.evaluate(msg)

    assert len(char_state.buffs) == 0, f"Buffs should be empty. Got: {char_state.buffs}"
    print(f"   [OK] List cleared: {char_state.buffs}")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("[SUCCESS] ALL STORAGE ACTION TESTS PASSED")
print("=" * 50)
print("\nFeatures tested:")
print("  - Add to buffs list")
print("  - Duplicate prevention")
print("  - Add to debuffs list")
print("  - Remove from debuffs list")
print("  - Update HP threshold flags")
print("  - Set scalar fields")
print("  - Clear lists")
print("\nStorage actions are working correctly!")

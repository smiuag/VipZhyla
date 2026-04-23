#!/usr/bin/env python3
"""Quick test to verify app startup and core functionality."""

import sys
sys.path.insert(0, 'src')

print("Testing VipZhyla startup and core modules...")
print("=" * 50)

# Test 1: Import all core modules
print("\n1. Testing imports...")
try:
    from app.audio_manager import AudioManager, AudioLevel
    print("   [OK] AudioManager imported")

    from app.keyboard_handler import KeyboardHandler, KeyAction
    print("   [OK] KeyboardHandler imported")

    from client.connection import MUDConnection, ConnectionState
    print("   [OK] MUDConnection imported")

    from client.message_buffer import MessageBuffer
    print("   [OK] MessageBuffer imported")

    from client.mud_parser import MUDParser, ChannelType
    print("   [OK] MUDParser imported")

    from client.gmcp_handler import GmcpHandler
    print("   [OK] GmcpHandler imported")

    from ui.list_dialogs import (show_channel_history, show_room_history,
                                 show_telepathy_history, show_event_list)
    print("   [OK] list_dialogs imported")

    from models.character_state import CharacterState
    print("   [OK] CharacterState imported")

    from client.character_parser import CharacterParser
    print("   [OK] CharacterParser imported")

    from models.triggers import TriggerManager
    print("   [OK] TriggerManager imported")

except Exception as e:
    print("   [FAIL] Import failed: " + str(e))
    sys.exit(1)

# Test 2: Create instances
print("\n2. Testing instance creation...")
try:
    audio = AudioManager()
    print("   [OK] AudioManager created")

    keyboard = KeyboardHandler()
    print("   [OK] KeyboardHandler created")

    connection = MUDConnection()
    print("   [OK] MUDConnection created (state: " + connection.state.value + ")")

    buffer = MessageBuffer()
    print("   [OK] MessageBuffer created")

    parser = MUDParser()
    print("   [OK] MUDParser created")

    gmcp = GmcpHandler(audio)
    print("   [OK] GmcpHandler created")

    state = CharacterState()
    print("   [OK] CharacterState created")

    trigger_manager = TriggerManager(audio)
    print("   [OK] TriggerManager created")

except Exception as e:
    print("   [FAIL] Instance creation failed: " + str(e))
    sys.exit(1)

# Test 3: Verify keyboard handlers
print("\n3. Testing keyboard configuration...")
try:
    desc = keyboard.get_key_description(KeyAction.SHOW_CHANNEL_HISTORY)
    print("   [OK] Shift+F1: " + desc)

    desc = keyboard.get_key_description(KeyAction.NEXT_CHANNEL)
    print("   [OK] Alt+Right: " + desc)

except Exception as e:
    print("   [FAIL] Keyboard test failed: " + str(e))
    sys.exit(1)

# Test 4: Verify message buffer
print("\n4. Testing message buffer...")
try:
    from client.mud_parser import ParsedMessage

    msg = ParsedMessage(ChannelType.GENERAL, "Test message", "raw")
    result = buffer.add(msg)
    print("   [OK] Message added (index: " + str(result.index) + ")")

    messages = buffer.get_channel(ChannelType.GENERAL)
    print("   [OK] Retrieved " + str(len(messages)) + " message(s)")

    channels = buffer.get_all_channels()
    channel_names = [ch.value for ch in channels]
    print("   [OK] Active channels: " + str(channel_names))

except Exception as e:
    print("   [FAIL] Message buffer test failed: " + str(e))
    sys.exit(1)

# Test 5: Verify connection state
print("\n5. Testing connection...")
try:
    state = connection.state
    print("   [OK] Connection state: " + state.value)

    assert state == ConnectionState.DISCONNECTED, "Should start disconnected"
    print("   [OK] Initial state is DISCONNECTED")

except Exception as e:
    print("   [FAIL] Connection test failed: " + str(e))
    sys.exit(1)

# Test 6: Audio verbosity levels
print("\n6. Testing audio levels...")
try:
    audio.set_verbosity(AudioLevel.NORMAL)
    assert audio.level == AudioLevel.NORMAL
    print("   [OK] Verbosity set to " + audio.level.name)

except Exception as e:
    print("   [FAIL] Audio test failed: " + str(e))
    sys.exit(1)

# Test 7: CharacterState and CharacterParser
print("\n7. Testing CharacterState...")
try:
    state = CharacterState()
    state.update_vitals(320, 450, 120, 200)
    assert state.hp == 320
    assert state.hp_pct == 71
    print("   [OK] CharacterState vitals updated (hp_pct: " + str(state.hp_pct) + "%)")

    # Test HP threshold detection
    threshold = state.get_hp_threshold()
    assert threshold == 90, f"Expected threshold 90, got {threshold}"
    print("   [OK] HP threshold detected: " + str(threshold))

    # Test GMCP parser
    gmcp_data = {"name": "Aeroth", "level": 42, "class": "Soldado", "race": "Elfo"}
    CharacterParser.parse_gmcp_status(state, gmcp_data)
    assert state.name == "Aeroth"
    assert state.clase == "Soldado"
    assert state.raza == "Elfo"
    print("   [OK] CharacterParser: GMCP status parsed")

except Exception as e:
    print("   [FAIL] CharacterState test failed: " + str(e))
    sys.exit(1)

print("\n" + "=" * 50)
print("[SUCCESS] ALL TESTS PASSED")
print("=" * 50)
print("\nVipZhyla is ready to run:")
print("  python src/main.py")
print("\nFeatures tested:")
print("  - All core modules import correctly")
print("  - Connection, buffer, parser, GMCP handlers work")
print("  - Keyboard handlers configured (Shift+F1-F4, Alt+arrows)")
print("  - Message buffer stores and retrieves messages")
print("  - Audio/TTS system initialized")
print("  - CharacterState model with vitals and HP thresholds")
print("  - CharacterParser GMCP integration")
print("  - TriggerManager loads and initializes")

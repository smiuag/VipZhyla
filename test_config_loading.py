#!/usr/bin/env python3
"""Configuration loading and validation tests (Phase 5.1).

Tests that MUD configuration can be loaded, validated, and used for
real server connections (when configured).
"""

import sys
sys.path.insert(0, 'src')

from config.config_loader import MudConfig

print("Configuration Loading Tests (Phase 5.1)")
print("=" * 70)

# ============================================================================
# Test 1: Load default configuration
# ============================================================================
print("\nTest 1: Load default configuration")
print("-" * 70)

try:
    config = MudConfig.load("src/config/mud_config.json")
    print("[OK] Configuration loaded from mud_config.json")
    print(f"    Server: {config.server.host}:{config.server.port}")
    print(f"    Character: {config.character.name}")
    print(f"    Encoding: {config.connection.encoding}")
    print(f"    TTS Enabled: {config.accessibility.tts_enabled}")
except Exception as e:
    print(f"[FAIL] Configuration load failed: {e}")
    sys.exit(1)

# ============================================================================
# Test 2: Validate configuration
# ============================================================================
print("\nTest 2: Validate configuration")
print("-" * 70)

is_valid, error = config.validate()
if is_valid:
    print("[OK] Configuration is valid")
else:
    print(f"[FAIL] Configuration validation failed: {error}")
    sys.exit(1)

# ============================================================================
# Test 3: Check if configuration is customized
# ============================================================================
print("\nTest 3: Check if configuration is customized")
print("-" * 70)

if config.is_configured():
    print("[OK] Configuration is customized (ready for MUD connection)")
else:
    print("[INFO] Configuration uses default values (needs customization for real MUD)")
    print("       Edit src/config/mud_config.json with your MUD server details")

# ============================================================================
# Test 4: Verify all configuration fields
# ============================================================================
print("\nTest 4: Verify all configuration fields")
print("-" * 70)

checks = [
    ("Server host", config.server.host is not None),
    ("Server port", 1 <= config.server.port <= 65535),
    ("Server timeout", config.server.timeout > 0),
    ("Reconnect attempts", config.server.reconnect_attempts > 0),
    ("Reconnect delay", config.server.reconnect_delay > 0),
    ("Character name", len(config.character.name) > 0),
    ("Character password", len(config.character.password) > 0),
    ("Connection encoding", config.connection.encoding in ["utf-8", "latin-1", "cp1252"]),
    ("GMCP enabled", isinstance(config.connection.gmcp_enabled, bool)),
    ("Telnet negotiation", isinstance(config.connection.telnet_negotiation, bool)),
    ("Auto load triggers", isinstance(config.automation.auto_load_triggers, bool)),
    ("Triggers file", len(config.automation.triggers_file) > 0),
    ("TTS enabled", isinstance(config.accessibility.tts_enabled, bool)),
    ("Verbosity level", config.accessibility.verbosity in ["SILENT", "MINIMAL", "NORMAL", "VERBOSE", "DEBUG"]),
]

passed = 0
for check_name, result in checks:
    status = "[OK]" if result else "[FAIL]"
    print(f"  {status} {check_name}")
    if result:
        passed += 1

# ============================================================================
# Test 5: Display current configuration
# ============================================================================
print("\nTest 5: Current configuration summary")
print("-" * 70)

print("\nServer Settings:")
print(f"  Host: {config.server.host}")
print(f"  Port: {config.server.port}")
print(f"  Timeout: {config.server.timeout}s")
print(f"  Reconnect: {config.server.reconnect_attempts} attempts, {config.server.reconnect_delay}s delay")

print("\nCharacter Settings:")
print(f"  Name: {config.character.name}")
print(f"  Class: {config.character.classe}")
print(f"  Race: {config.character.race}")
print(f"  Password: {'*' * len(config.character.password)}")

print("\nConnection Settings:")
print(f"  Encoding: {config.connection.encoding}")
print(f"  Line Ending: {repr(config.connection.line_ending)}")
print(f"  GMCP: {config.connection.gmcp_enabled}")
print(f"  Telnet Negotiation: {config.connection.telnet_negotiation}")

print("\nAutomation Settings:")
print(f"  Auto Load Triggers: {config.automation.auto_load_triggers}")
print(f"  Triggers File: {config.automation.triggers_file}")
print(f"  Auto Start Timers: {config.automation.auto_start_timers}")
print(f"  Log Output: {config.automation.log_all_output}")

print("\nAccessibility Settings:")
print(f"  TTS Enabled: {config.accessibility.tts_enabled}")
print(f"  Verbosity: {config.accessibility.verbosity}")
print(f"  Announce Connection: {config.accessibility.announce_connection}")
print(f"  Announce Disconnection: {config.accessibility.announce_disconnection}")
print(f"  Announce Errors: {config.accessibility.announce_errors}")

# ============================================================================
# Test 6: Configuration for next steps
# ============================================================================
print("\nTest 6: Configuration readiness for Phase 5.1")
print("-" * 70)

next_steps = []

if not config.is_configured():
    next_steps.append("1. Edit src/config/mud_config.json with your MUD server address")
    next_steps.append("   - Set 'host' to your MUD server (e.g., 'reinos.example.com')")
    next_steps.append("   - Set 'port' to the MUD port (e.g., 4000)")
    next_steps.append("   - Set 'name' to your character name")
    next_steps.append("   - Set 'password' to your account password")
else:
    next_steps.append("1. Configuration is ready for MUD connection")

next_steps.extend([
    "2. Verify screen reader is running (NVDA: Win+Ctrl+N)",
    "3. Run: python src/main.py",
    "4. Click [Conectar] to connect to MUD",
    "5. Verify TTS announcements and keyboard navigation",
    "6. Test triggers by engaging in game activity"
])

for step in next_steps:
    print(f"  {step}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
if passed == len(checks):
    print(f"[SUCCESS] Configuration Validation Complete - {passed}/{len(checks)} checks passed")
else:
    print(f"[PARTIAL] Configuration Validation - {passed}/{len(checks)} checks passed")
print("=" * 70)

print(f"\nConfiguration Status: {'READY' if config.is_configured() else 'NEEDS SETUP'}")
print(f"Next Phase: Phase 5.1 - Real NVDA/JAWS Testing with Live MUD")

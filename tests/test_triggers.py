"""
Tests for trigger, alias, and timer system (logic layer).
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.client.mud_parser import ParsedMessage, ChannelType
from src.models.triggers import (
    TriggerManager, Trigger, Alias, Timer, TriggerAction, ActionType
)
from src.app.audio_manager import AudioManager


@pytest.fixture
def audio():
    """Provide AudioManager instance."""
    return AudioManager()


@pytest.fixture
def trigger_manager(audio):
    """Provide TriggerManager instance."""
    mgr = TriggerManager(audio)
    # Use temp file for testing
    mgr.SAVE_PATH = Path(tempfile.gettempdir()) / "test_triggers.json"
    yield mgr
    # Cleanup
    if mgr.SAVE_PATH.exists():
        mgr.SAVE_PATH.unlink()


class TestTriggerMatching:
    """Test trigger pattern matching."""

    def test_trigger_matches_substring(self, trigger_manager):
        """Substring pattern should match."""
        trigger = Trigger(
            id="t1",
            name="Test",
            pattern="hola",
            is_regex=False,
            actions=[TriggerAction(ActionType.TTS, "Saludo detectado")]
        )
        trigger_manager.add_trigger(trigger)

        parsed = ParsedMessage(ChannelType.GENERAL, "Alguien dice hola", "[Sala] Alguien dice hola")

        # Should not raise, and should match
        gagged = trigger_manager.evaluate(parsed)
        assert gagged == False

    def test_trigger_matches_regex(self, trigger_manager):
        """Regex pattern should match."""
        trigger = Trigger(
            id="t1",
            name="Test",
            pattern=r"^\[Bando\]",
            is_regex=True,
            actions=[TriggerAction(ActionType.TTS, "Mensaje en bando")]
        )
        trigger_manager.add_trigger(trigger)

        parsed = ParsedMessage(ChannelType.BANDO, "Alguien dice algo", "[Bando] Alguien dice algo")
        gagged = trigger_manager.evaluate(parsed)
        assert gagged == False

    def test_trigger_case_insensitive(self, trigger_manager):
        """Matching should be case-insensitive."""
        trigger = Trigger(
            id="t1",
            name="Test",
            pattern="HOLA",
            is_regex=False,
            actions=[TriggerAction(ActionType.TTS, "")]
        )
        trigger_manager.add_trigger(trigger)

        parsed = ParsedMessage(ChannelType.GENERAL, "alguien dice hola", "alguien dice hola")
        gagged = trigger_manager.evaluate(parsed)
        assert gagged == False

    def test_trigger_disabled_not_fires(self, trigger_manager):
        """Disabled trigger should not fire."""
        trigger = Trigger(
            id="t1",
            name="Test",
            pattern="hola",
            is_regex=False,
            enabled=False,
            actions=[TriggerAction(ActionType.TTS, "Should not fire")]
        )
        trigger_manager.add_trigger(trigger)

        parsed = ParsedMessage(ChannelType.GENERAL, "hola", "hola")
        gagged = trigger_manager.evaluate(parsed)
        assert gagged == False

    def test_trigger_no_match(self, trigger_manager):
        """Non-matching pattern should not fire."""
        trigger = Trigger(
            id="t1",
            name="Test",
            pattern="xyz",
            is_regex=False,
            actions=[TriggerAction(ActionType.TTS, "")]
        )
        trigger_manager.add_trigger(trigger)

        parsed = ParsedMessage(ChannelType.GENERAL, "hola", "hola")
        gagged = trigger_manager.evaluate(parsed)
        assert gagged == False


class TestGagAction:
    """Test gag (hide line) action."""

    def test_gag_returns_true(self, trigger_manager):
        """GAG action should cause evaluate() to return True."""
        trigger = Trigger(
            id="t1",
            name="Test",
            pattern="spam",
            is_regex=False,
            actions=[TriggerAction(ActionType.GAG, "")]
        )
        trigger_manager.add_trigger(trigger)

        parsed = ParsedMessage(ChannelType.GENERAL, "spam spam spam", "spam spam spam")
        gagged = trigger_manager.evaluate(parsed)
        assert gagged == True

    def test_multiple_actions_with_gag(self, trigger_manager):
        """Multiple actions including GAG should return True."""
        trigger = Trigger(
            id="t1",
            name="Test",
            pattern="spam",
            is_regex=False,
            actions=[
                TriggerAction(ActionType.TTS, "Spammer detectado"),
                TriggerAction(ActionType.GAG, "")
            ]
        )
        trigger_manager.add_trigger(trigger)

        parsed = ParsedMessage(ChannelType.GENERAL, "spam", "spam")
        gagged = trigger_manager.evaluate(parsed)
        assert gagged == True


class TestAliasExpansion:
    """Test alias command expansion."""

    def test_alias_expansion(self, trigger_manager):
        """Simple alias should expand."""
        alias = Alias(id="a1", abbreviation="h", expansion="help")
        trigger_manager.add_alias(alias)

        expanded = trigger_manager.expand_alias("h")
        assert expanded == "help"

    def test_alias_expansion_with_args(self, trigger_manager):
        """Alias with arguments should preserve them."""
        alias = Alias(id="a1", abbreviation="e", expansion="examine")
        trigger_manager.add_alias(alias)

        expanded = trigger_manager.expand_alias("e potion")
        assert expanded == "examine potion"

    def test_alias_case_insensitive(self, trigger_manager):
        """Alias matching should be case-insensitive."""
        alias = Alias(id="a1", abbreviation="h", expansion="help")
        trigger_manager.add_alias(alias)

        expanded = trigger_manager.expand_alias("H")
        assert expanded == "help"

    def test_alias_no_match(self, trigger_manager):
        """Non-matching command should return unchanged."""
        alias = Alias(id="a1", abbreviation="h", expansion="help")
        trigger_manager.add_alias(alias)

        expanded = trigger_manager.expand_alias("help")
        assert expanded == "help"

    def test_alias_disabled_not_expands(self, trigger_manager):
        """Disabled alias should not expand."""
        alias = Alias(id="a1", abbreviation="h", expansion="help", enabled=False)
        trigger_manager.add_alias(alias)

        expanded = trigger_manager.expand_alias("h")
        assert expanded == "h"

    def test_multiple_aliases(self, trigger_manager):
        """Multiple aliases should all work."""
        trigger_manager.add_alias(Alias(id="a1", abbreviation="h", expansion="help"))
        trigger_manager.add_alias(Alias(id="a2", abbreviation="l", expansion="look"))

        assert trigger_manager.expand_alias("h") == "help"
        assert trigger_manager.expand_alias("l") == "look"


class TestSaveAndLoad:
    """Test persistence."""

    def test_save_and_load_triggers(self, trigger_manager):
        """Triggers should persist and reload."""
        trigger = Trigger(
            id="t1",
            name="My Trigger",
            pattern="test",
            is_regex=False,
            actions=[TriggerAction(ActionType.TTS, "Test TTS")],
            enabled=True
        )
        trigger_manager.add_trigger(trigger)

        # Create new manager and load
        mgr2 = TriggerManager(trigger_manager.audio)
        mgr2.SAVE_PATH = trigger_manager.SAVE_PATH
        mgr2.load()

        assert len(mgr2.triggers) == 1
        assert mgr2.triggers[0].id == "t1"
        assert mgr2.triggers[0].name == "My Trigger"
        assert mgr2.triggers[0].pattern == "test"

    def test_save_and_load_aliases(self, trigger_manager):
        """Aliases should persist and reload."""
        alias = Alias(id="a1", abbreviation="h", expansion="help")
        trigger_manager.add_alias(alias)

        mgr2 = TriggerManager(trigger_manager.audio)
        mgr2.SAVE_PATH = trigger_manager.SAVE_PATH
        mgr2.load()

        assert len(mgr2.aliases) == 1
        assert mgr2.aliases[0].abbreviation == "h"
        assert mgr2.aliases[0].expansion == "help"

    def test_save_and_load_timers(self, trigger_manager):
        """Timers should persist and reload."""
        timer = Timer(
            id="tm1",
            name="My Timer",
            interval=30,
            actions=[TriggerAction(ActionType.TTS, "Timer fired")]
        )
        trigger_manager.add_timer(timer)

        mgr2 = TriggerManager(trigger_manager.audio)
        mgr2.SAVE_PATH = trigger_manager.SAVE_PATH
        mgr2.load()

        assert len(mgr2.timers) == 1
        assert mgr2.timers[0].name == "My Timer"
        assert mgr2.timers[0].interval == 30

    def test_json_format_valid(self, trigger_manager):
        """JSON file should be valid and readable."""
        trigger = Trigger(
            id="t1",
            name="Test",
            pattern="test",
            is_regex=False,
            actions=[TriggerAction(ActionType.TTS, "Test")]
        )
        trigger_manager.add_trigger(trigger)

        # Load and verify JSON structure
        with open(trigger_manager.SAVE_PATH) as f:
            data = json.load(f)

        assert "triggers" in data
        assert "aliases" in data
        assert "timers" in data
        assert len(data["triggers"]) == 1


class TestAddRemove:
    """Test adding and removing items."""

    def test_add_trigger(self, trigger_manager):
        """Adding a trigger should store it."""
        trigger = Trigger(id="t1", name="Test", pattern="x", actions=[])
        trigger_manager.add_trigger(trigger)

        assert len(trigger_manager.triggers) == 1
        assert trigger_manager.triggers[0].id == "t1"

    def test_remove_trigger(self, trigger_manager):
        """Removing a trigger should delete it."""
        trigger = Trigger(id="t1", name="Test", pattern="x", actions=[])
        trigger_manager.add_trigger(trigger)
        trigger_manager.remove_trigger("t1")

        assert len(trigger_manager.triggers) == 0

    def test_update_trigger(self, trigger_manager):
        """Adding a trigger with same ID should update it."""
        t1 = Trigger(id="t1", name="Test1", pattern="x", actions=[])
        trigger_manager.add_trigger(t1)

        t2 = Trigger(id="t1", name="Test2", pattern="y", actions=[])
        trigger_manager.add_trigger(t2)

        assert len(trigger_manager.triggers) == 1
        assert trigger_manager.triggers[0].name == "Test2"

    def test_new_id_generates_unique(self, trigger_manager):
        """new_id() should generate unique IDs."""
        id1 = trigger_manager.new_id()
        id2 = trigger_manager.new_id()
        assert id1 != id2

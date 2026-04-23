"""
Tests for keyboard handler module
"""

import pytest
from src.app.keyboard_handler import KeyboardHandler, KeyAction


def test_keyboard_handler_init():
    """Test keyboard handler initialization."""
    handler = KeyboardHandler()
    assert handler is not None
    assert len(handler.key_map) > 0


def test_keyboard_handler_register():
    """Test registering keyboard handler."""
    handler = KeyboardHandler()
    called = []

    def callback(event):
        called.append(True)

    handler.register_handler(KeyAction.MOVE_WEST, callback)
    assert KeyAction.MOVE_WEST in handler.handlers


def test_key_description():
    """Test getting key descriptions."""
    handler = KeyboardHandler()
    desc = handler.get_key_description(KeyAction.MOVE_WEST)
    assert "Alt+U" in desc
    assert "West" in desc

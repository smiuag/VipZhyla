"""
Tests for audio manager module
"""

import pytest
from src.app.audio_manager import AudioManager, AudioLevel


def test_audio_manager_init():
    """Test audio manager initialization."""
    manager = AudioManager()
    assert manager is not None
    assert manager.level == AudioLevel.NORMAL
    assert manager.enabled


def test_audio_manager_set_verbosity():
    """Test setting verbosity level."""
    manager = AudioManager()
    manager.set_verbosity(AudioLevel.VERBOSE)
    assert manager.level == AudioLevel.VERBOSE


def test_audio_manager_toggle_verbosity():
    """Test toggling verbosity."""
    manager = AudioManager()
    initial = manager.level
    manager.toggle_verbosity()
    assert manager.level != initial
    manager.toggle_verbosity()
    assert manager.level == initial

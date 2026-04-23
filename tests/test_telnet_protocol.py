"""
Tests for Telnet protocol handler.
"""

import pytest
from src.client.telnet_protocol import TelnetProcessor, TelnetState, IAC, DO, GMCP, DONT


class TestTelnetProcessor:
    """Test Telnet protocol processing."""

    def test_plain_text_passthrough(self):
        """Plain text should pass through unchanged."""
        processor = TelnetProcessor()
        text_bytes = b"Hello, world!"
        clean_text, gmcp_data = processor.process(text_bytes)

        assert clean_text == "Hello, world!"
        assert gmcp_data == []

    def test_strips_ansi_codes(self):
        """ANSI escape codes should be stripped."""
        processor = TelnetProcessor()
        # ESC[32m is green color, ESC[0m is reset
        text_bytes = b"\x1b[32mGreen text\x1b[0m"
        clean_text, gmcp_data = processor.process(text_bytes)

        assert clean_text == "Green text"
        assert gmcp_data == []

    def test_ansi_with_multiple_params(self):
        """ANSI codes with multiple parameters should be stripped."""
        processor = TelnetProcessor()
        # ESC[1;32m is bold green
        text_bytes = b"\x1b[1;32mBold green\x1b[0m"
        clean_text, gmcp_data = processor.process(text_bytes)

        assert clean_text == "Bold green"

    def test_gmcp_simple_hello(self):
        """Parse simple GMCP Core.Hello."""
        processor = TelnetProcessor()

        # IAC SB GMCP "Core.Hello" {"version": "1.0"} IAC SE
        # In bytes: 255 250 201 ... 255 240
        gmcp_bytes = (
            bytes([IAC, 250, GMCP]) +
            b'Core.Hello {"version": "1.0"}' +
            bytes([IAC, 240])
        )

        clean_text, gmcp_data = processor.process(gmcp_bytes)

        assert len(gmcp_data) == 1
        module, data = gmcp_data[0]
        assert module == "Core.Hello"
        assert data == {"version": "1.0"}

    def test_iac_will_gmcp_triggers_do_response(self):
        """Server WILL GMCP should trigger DO GMCP response."""
        responses = []

        def capture_response(data):
            responses.append(data)

        processor = TelnetProcessor(send_raw_callback=capture_response)

        # IAC WILL GMCP
        iac_will_gmcp = bytes([IAC, 251, GMCP])
        processor.process(iac_will_gmcp)

        assert len(responses) == 1
        response = responses[0]
        assert response == bytes([IAC, DO, GMCP])

    def test_text_with_ansi_and_gmcp(self):
        """Mixed text with ANSI and GMCP should handle both."""
        processor = TelnetProcessor()

        # Normal text with ANSI
        text_part = b"Hello\x1b[0m World"
        # GMCP data
        gmcp_part = bytes([IAC, 250, GMCP]) + b'Test {"ok": true}' + bytes([IAC, 240])

        combined = text_part + gmcp_part

        clean_text, gmcp_data = processor.process(combined)

        assert "Hello World" in clean_text
        assert len(gmcp_data) == 1
        assert gmcp_data[0][0] == "Test"

    def test_reset_clears_state(self):
        """Reset should clear parser state."""
        processor = TelnetProcessor()
        processor.state = TelnetState.SB_GMCP
        processor.sb_data = bytearray(b"some data")

        processor.reset()

        assert processor.state == TelnetState.TEXT
        assert processor.sb_data == bytearray()

    def test_invalid_json_in_gmcp_ignored(self):
        """Invalid JSON in GMCP should be silently ignored."""
        processor = TelnetProcessor()

        # GMCP with malformed JSON
        gmcp_bytes = (
            bytes([IAC, 250, GMCP]) +
            b'Test {invalid json}' +
            bytes([IAC, 240])
        )

        clean_text, gmcp_data = processor.process(gmcp_bytes)

        # Should not crash, should have no GMCP data
        assert gmcp_data == []

    def test_multiline_text(self):
        """Handle text with newlines and ANSI."""
        processor = TelnetProcessor()

        text_bytes = b"Line 1\x1b[0m\nLine 2\x1b[32m\nLine 3"
        clean_text, gmcp_data = processor.process(text_bytes)

        assert "Line 1\nLine 2\nLine 3" == clean_text

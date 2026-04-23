"""
Telnet protocol handler with GMCP support.

Handles:
- Telnet negotiation (IAC WILL/WONT/DO/DONT)
- GMCP subnegotiation (IAC SB GMCP ... IAC SE)
- ANSI escape code stripping
- Text extraction from raw bytes
"""

import json
import re
from enum import Enum
from typing import Callable, Optional


# Telnet protocol constants
IAC = 255   # Interpret As Command
WILL = 251  # WILL
WONT = 252  # WONT
DO = 253    # DO
DONT = 254  # DONT
SB = 250    # Subnegotiation Begin
SE = 240    # Subnegotiation End

# Option codes
GMCP = 201  # GMCP option


class TelnetState(Enum):
    """State machine states for Telnet protocol parsing."""
    TEXT = "text"              # Normal text
    IAC = "iac"                # Received IAC, waiting for command
    SB_GMCP = "sb_gmcp"        # In GMCP subnegotiation (IAC SB GMCP ...)
    DO_DONT_WILL_WONT = "do_dont_will_wont"  # Waiting for option after DO/DONT/WILL/WONT


class TelnetProcessor:
    """
    Processes raw Telnet bytes and extracts text + GMCP data.

    Automatically responds to Telnet negotiations:
    - WILL GMCP → sends DO GMCP
    - WILL X (other) → sends DONT X
    - DO X → sends WONT X
    """

    # ANSI escape code pattern: ESC[0-9;]*[mGKHF]
    ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*[mGKHF]')

    def __init__(self, send_raw_callback: Optional[Callable[[bytes], None]] = None, encoding: str = "utf-8"):
        """
        Initialize Telnet processor.

        Args:
            send_raw_callback: Called with bytes when Telnet response is needed.
                              If None, responses are silently dropped.
            encoding: Character encoding for text decoding (default: utf-8)
        """
        self.send_raw = send_raw_callback or (lambda x: None)
        self.encoding = encoding
        self.state = TelnetState.TEXT
        self.text_buffer = ""
        self.text_bytes = bytearray()  # Accumulate raw bytes for proper UTF-8 decoding
        self.iac_buffer = []
        self.sb_data = bytearray()
        self.sb_option = None
        self.gmcp_modules = {}  # module -> data dict, for deduplication

    def process(self, raw_bytes: bytes) -> tuple[str, list[tuple[str, dict]]]:
        """
        Process raw bytes from MUD server.

        Returns:
            (clean_text, [(module, data), ...])
        """
        text_output = []
        gmcp_output = []

        for byte in raw_bytes:
            if self.state == TelnetState.TEXT:
                self._handle_text_state(byte, text_output, gmcp_output)
            elif self.state == TelnetState.IAC:
                self._handle_iac_state(byte)
            elif self.state == TelnetState.SB_GMCP:
                self._handle_sb_gmcp_state(byte, gmcp_output)
            elif self.state == TelnetState.DO_DONT_WILL_WONT:
                self._handle_command_state(byte)

        # Flush any remaining accumulated text bytes
        if self.text_bytes:
            try:
                text = self.text_bytes.decode(self.encoding, errors='replace')
                text_output.append(text)
            except Exception:
                text_output.append(self.text_bytes.decode('utf-8', errors='replace'))
            self.text_bytes = bytearray()

        # Strip ANSI codes from accumulated text
        clean_text = self._strip_ansi(''.join(text_output))

        return clean_text, gmcp_output

    def _handle_text_state(self, byte: int, text_output: list, gmcp_output: list):
        """Handle normal text byte."""
        if byte == IAC:
            # IAC found - flush accumulated text bytes and switch to IAC state
            if self.text_bytes:
                try:
                    text = self.text_bytes.decode(self.encoding, errors='replace')
                    text_output.append(text)
                except Exception:
                    text_output.append(self.text_bytes.decode('utf-8', errors='replace'))
                self.text_bytes = bytearray()
            self.state = TelnetState.IAC
        else:
            # Accumulate byte for later decoding
            self.text_bytes.append(byte)

    def _handle_iac_state(self, byte: int):
        """Handle byte after IAC."""
        if byte == WILL:
            self.state = TelnetState.DO_DONT_WILL_WONT
            self.iac_buffer = ['WILL']
        elif byte == WONT:
            self.state = TelnetState.DO_DONT_WILL_WONT
            self.iac_buffer = ['WONT']
        elif byte == DO:
            self.state = TelnetState.DO_DONT_WILL_WONT
            self.iac_buffer = ['DO']
        elif byte == DONT:
            self.state = TelnetState.DO_DONT_WILL_WONT
            self.iac_buffer = ['DONT']
        elif byte == SB:
            # Subnegotiation begin - next byte is the option code (e.g., GMCP=201)
            self.state = TelnetState.SB_GMCP
            self.sb_data = bytearray()
            self.sb_option = None
        elif byte == IAC:
            # Escaped IAC (0xff 0xff means a literal 0xff byte)
            self.state = TelnetState.TEXT
        else:
            # Unknown command, return to text
            self.state = TelnetState.TEXT

    def _handle_command_state(self, byte: int):
        """Handle option byte after DO/DONT/WILL/WONT."""
        command = self.iac_buffer[0]

        if command == 'WILL':
            self._handle_will(byte)
        elif command == 'WONT':
            self._handle_wont(byte)
        elif command == 'DO':
            self._handle_do(byte)
        elif command == 'DONT':
            self._handle_dont(byte)

        self.state = TelnetState.TEXT
        self.iac_buffer = []

    def _handle_will(self, option: int):
        """Server wants to enable option."""
        if option == GMCP:
            # Server will send GMCP, we agree
            response = bytes([IAC, DO, GMCP])
            self.send_raw(response)
        else:
            # We don't support other options, say DONT
            response = bytes([IAC, DONT, option])
            self.send_raw(response)

    def _handle_wont(self, option: int):
        """Server won't enable option."""
        # Just acknowledge
        pass

    def _handle_do(self, option: int):
        """Server wants us to enable option."""
        # We don't actively enable anything
        response = bytes([IAC, WONT, option])
        self.send_raw(response)

    def _handle_dont(self, option: int):
        """Server wants us to disable option."""
        # Just acknowledge
        pass

    def _handle_sb_gmcp_state(self, byte: int, gmcp_output: list):
        """Handle byte during GMCP subnegotiation.

        Format: IAC SB GMCP "Module" data IAC SE
        First byte after SB is the option code (GMCP=201), then module name and data.
        """
        if self.sb_option is None and byte != IAC:
            # First byte is the option code (should be GMCP=201)
            self.sb_option = byte
        elif byte == IAC:
            # Potential end of subnegotiation (IAC SE)
            # Mark this with a sentinel, will check next byte
            self.sb_data.append(byte)
        elif byte == SE and len(self.sb_data) > 0 and self.sb_data[-1] == IAC:
            # End of subnegotiation: IAC SE
            # Remove the trailing IAC from sb_data
            self.sb_data = self.sb_data[:-1]

            # Parse GMCP data if option is GMCP
            if self.sb_option == GMCP:
                self._parse_gmcp(gmcp_output)

            self.state = TelnetState.TEXT
            self.sb_data = bytearray()
            self.sb_option = None
        else:
            # Accumulate subnegotiation data (skip if we haven't seen option code yet)
            if self.sb_option is not None:
                self.sb_data.append(byte)

    def _parse_gmcp(self, gmcp_output: list):
        """Parse accumulated GMCP data."""
        try:
            data_str = self.sb_data.decode('utf-8', errors='replace')

            # GMCP format: "Module.Submodule" followed by JSON data
            # Example: "Char.Vitals" {"hp": 100, "maxhp": 200}
            parts = data_str.split(None, 1)  # Split on first whitespace

            if len(parts) < 1:
                return

            module = parts[0]
            json_str = parts[1] if len(parts) > 1 else "{}"

            try:
                data = json.loads(json_str)
                gmcp_output.append((module, data))
            except json.JSONDecodeError:
                # Invalid JSON, ignore
                pass
        except Exception:
            # Any error during parsing, just skip
            pass

    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes from text."""
        return self.ANSI_PATTERN.sub('', text)

    def reset(self):
        """Reset parser state (useful for debugging or reconnection)."""
        self.state = TelnetState.TEXT
        self.text_buffer = ""
        self.iac_buffer = []
        self.sb_data = bytearray()
        self.sb_option = None

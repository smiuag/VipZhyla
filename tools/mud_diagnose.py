#!/usr/bin/env python3
"""
MUD Server Diagnostics Tool

Connect to a MUD server and display diagnostic information:
- Connection status
- GMCP module support
- Sample text and GMCP data
- Character encoding handling

Usage:
    python tools/mud_diagnose.py [host] [port]

Example:
    python tools/mud_diagnose.py reinosdeleyenda.com 23
"""

import sys
import time
sys.path.insert(0, '.')

from src.client.connection import MUDConnection, ConnectionState


class MUDDiagnostics:
    """Diagnostic tool for MUD servers."""

    def __init__(self, host: str = "reinosdeleyenda.com", port: int = 23):
        """Initialize diagnostics."""
        self.host = host
        self.port = port
        self.connection = MUDConnection(encoding="UTF-8")

        # Counters
        self.text_lines = 0
        self.gmcp_modules = {}
        self.sample_text = []
        self.sample_gmcp = []

    def run(self):
        """Run diagnostics."""
        print(f"VipZhyla MUD Server Diagnostics")
        print(f"=" * 50)
        print(f"Target: {self.host}:{self.port}")
        print(f"Encoding: {self.connection.encoding}")
        print()

        # Setup callbacks
        self.connection.set_data_callback(self._on_data)
        self.connection.set_gmcp_callback(self._on_gmcp)
        self.connection.set_state_callback(self._on_state)

        # Connect
        print("Connecting...")
        if not self.connection.connect(self.host, self.port):
            print("ERROR: Failed to connect")
            return False

        # Wait for data
        print("Waiting for server response (10 seconds)...")
        for i in range(10):
            time.sleep(1)
            if self.text_lines > 5 or self.gmcp_modules:
                break
            print(".", end="", flush=True)

        print()
        print()

        # Disconnect
        print("Disconnecting...")
        self.connection.disconnect()

        # Report
        self._report()
        return True

    def _on_data(self, text: str):
        """Callback for text data."""
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                self.text_lines += 1
                if len(self.sample_text) < 10:
                    self.sample_text.append(line)

    def _on_gmcp(self, module: str, data: dict):
        """Callback for GMCP data."""
        if module not in self.gmcp_modules:
            self.gmcp_modules[module] = []

        self.gmcp_modules[module].append(data)

        if len(self.sample_gmcp) < 5:
            self.sample_gmcp.append((module, data))

    def _on_state(self, state: ConnectionState, message: str):
        """Callback for state changes."""
        print(f"[{state.value.upper()}] {message}")

    def _report(self):
        """Print diagnostic report."""
        print()
        print("DIAGNOSTIC REPORT")
        print("=" * 50)

        # Connection status
        print(f"Connection Status: {self.connection.state.value.upper()}")
        print()

        # Text data
        print(f"Text Lines Received: {self.text_lines}")
        if self.sample_text:
            print("Sample Text (first 10 lines):")
            for i, line in enumerate(self.sample_text, 1):
                print(f"  {i}. {line[:70]}...")
        print()

        # GMCP support
        if self.gmcp_modules:
            print(f"GMCP Support: YES ✓")
            print(f"Modules Received: {len(self.gmcp_modules)}")
            for module in sorted(self.gmcp_modules.keys()):
                count = len(self.gmcp_modules[module])
                print(f"  - {module} (x{count})")
            print()

            if self.sample_gmcp:
                print("Sample GMCP Data (first 5 modules):")
                for module, data in self.sample_gmcp:
                    print(f"  Module: {module}")
                    for key, value in data.items():
                        if isinstance(value, (str, int, float, bool)):
                            print(f"    {key}: {value}")
                        else:
                            print(f"    {key}: {type(value).__name__}")
                print()
        else:
            print(f"GMCP Support: NO ✗")
            print("(Server may not support GMCP, or no GMCP data received yet)")
            print()

        # Recommendations
        print("RECOMMENDATIONS:")
        if self.text_lines > 0:
            print("  ✓ Server is responding to text connections")
        else:
            print("  ✗ No text data received - server may be slow or incompatible")

        if self.gmcp_modules:
            print("  ✓ Server supports GMCP - advanced features available")
        else:
            print("  ✓ Text-only mode - will use pattern matching for channels")

        if "Char.Vitals" in self.gmcp_modules:
            print("  ✓ Char.Vitals available - health tracking enabled")

        if "Room.Info" in self.gmcp_modules:
            print("  ✓ Room.Info available - location tracking enabled")

        if "Comm.Channel" in self.gmcp_modules:
            print("  ✓ Comm.Channel available - channel identification via GMCP")

        print()
        print("=" * 50)
        print("Diagnostics Complete")


def main():
    """Main entry point."""
    host = "reinosdeleyenda.com"
    port = 23

    if len(sys.argv) > 1:
        host = sys.argv[1]

    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"ERROR: Invalid port '{sys.argv[2]}'")
            sys.exit(1)

    diag = MUDDiagnostics(host, port)
    success = diag.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

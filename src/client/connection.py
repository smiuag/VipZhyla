"""
MUD server connection handler.

Manages Telnet connection using socket and spawns receive thread
to process incoming bytes via TelnetProcessor.

Thread-safe callbacks for:
- Text data (cleaned text)
- GMCP data (structured JSON)
- Connection state changes
"""

import socket
import threading
from enum import Enum
from typing import Callable, Optional

from .telnet_protocol import TelnetProcessor


class ConnectionState(Enum):
    """Connection state."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class MUDConnection:
    """
    Manages connection to MUD server via Telnet.

    Spawns daemon thread for receiving data.
    Callbacks are invoked from receive thread.
    """

    def __init__(self, encoding: str = "UTF-8"):
        """
        Initialize connection.

        Args:
            encoding: Text encoding (UTF-8, ISO-8859-1, etc.)
        """
        self.encoding = encoding
        self.state = ConnectionState.DISCONNECTED

        self.socket: Optional[socket.socket] = None
        self.receive_thread: Optional[threading.Thread] = None
        self.running = False

        # Callbacks
        self.on_data: Optional[Callable[[str], None]] = None
        self.on_gmcp: Optional[Callable[[str, dict], None]] = None
        self.on_state: Optional[Callable[[ConnectionState, str], None]] = None

        # Telnet processor (will be initialized with encoding in set_encoding method)
        self.telnet = TelnetProcessor(send_raw_callback=self._send_raw, encoding=encoding)

    def connect(self, host: str, port: int) -> bool:
        """
        Connect to MUD server.

        Args:
            host: Hostname or IP
            port: Port number (usually 23 for Telnet)

        Returns:
            True if connection started, False otherwise
        """
        if self.state != ConnectionState.DISCONNECTED:
            return False

        try:
            print(f"[CONNECTION] Connecting to {host}:{port}...")
            self._set_state(ConnectionState.CONNECTING, f"Conectando a {host}:{port}...")

            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)  # 30s connect timeout
            print(f"[CONNECTION] Socket created, attempting connect...")

            # Connect
            self.socket.connect((host, port))
            print(f"[CONNECTION] Connected successfully!")

            # Send GMCP negotiation
            iac_do_gmcp = bytes([255, 253, 201])  # IAC DO GMCP
            self.socket.sendall(iac_do_gmcp)
            print(f"[CONNECTION] GMCP negotiation sent")

            # Start receive thread
            self.running = True
            self.receive_thread = threading.Thread(
                target=self._receive_loop,
                daemon=True
            )
            self.receive_thread.start()
            print(f"[CONNECTION] Receive thread started")

            self._set_state(ConnectionState.CONNECTED, f"Conectado a {host}:{port}")
            return True

        except Exception as e:
            print(f"[CONNECTION ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            self.socket = None
            self._set_state(ConnectionState.ERROR, f"Error de conexión: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from server."""
        if self.state in (ConnectionState.DISCONNECTED, ConnectionState.CONNECTING):
            return

        self.running = False

        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None

        if self.receive_thread and self.receive_thread != threading.current_thread():
            self.receive_thread.join(timeout=2)
            self.receive_thread = None

        self._set_state(ConnectionState.DISCONNECTED, "Desconectado")

    def set_encoding(self, encoding: str):
        """
        Change character encoding (for dynamic preference changes).

        Args:
            encoding: Character encoding (utf-8, iso-8859-1, cp1252, etc.)
        """
        self.encoding = encoding
        self.telnet.encoding = encoding

    def send(self, text: str):
        """
        Send text command to server.

        Appends CRLF and encodes with configured encoding.

        Args:
            text: Command text (without line ending)
        """
        if self.state != ConnectionState.CONNECTED:
            return

        try:
            # Add line ending
            text_with_crlf = text + "\r\n"

            # Encode
            data = text_with_crlf.encode(self.encoding, errors='replace')

            # Send
            self.socket.sendall(data)
        except Exception as e:
            self._set_state(ConnectionState.ERROR, f"Error enviando: {str(e)}")
            self.disconnect()

    def send_raw(self, data: bytes):
        """
        Send raw bytes (for Telnet protocol responses).

        Args:
            data: Raw bytes to send
        """
        if self.state != ConnectionState.CONNECTED or not self.socket:
            return

        try:
            self.socket.sendall(data)
        except Exception:
            pass

    def set_data_callback(self, callback: Callable[[str], None]):
        """Register callback for text data."""
        self.on_data = callback

    def set_gmcp_callback(self, callback: Callable[[str, dict], None]):
        """Register callback for GMCP data (module, data)."""
        self.on_gmcp = callback

    def set_state_callback(self, callback: Callable[[ConnectionState, str], None]):
        """Register callback for state changes (state, message)."""
        self.on_state = callback

    def shutdown(self):
        """Graceful shutdown (for cleanup)."""
        self.disconnect()

    def __del__(self):
        """Ensure socket is closed on garbage collection."""
        try:
            self.shutdown()
        except Exception:
            pass

    # Private methods

    def _receive_loop(self):
        """
        Receive loop (runs in daemon thread).

        Continuously reads from socket, processes via TelnetProcessor,
        invokes callbacks for text and GMCP data.
        """
        print(f"[RECEIVE] Loop started")
        try:
            while self.running and self.socket:
                try:
                    # Receive data
                    print(f"[RECEIVE] Waiting for data...")
                    raw_bytes = self.socket.recv(4096)
                    print(f"[RECEIVE] Got {len(raw_bytes)} bytes: {repr(raw_bytes[:100])}")

                    if not raw_bytes:
                        # Connection closed by server
                        print(f"[RECEIVE] Server closed connection")
                        break

                    # Process via Telnet protocol
                    text, gmcp_list = self.telnet.process(raw_bytes)
                    print(f"[RECEIVE] Processed: text={repr(text[:80] if text else '')}, gmcp={len(gmcp_list)} msgs")

                    # Decode text
                    if text:
                        # text is already a str from telnet_protocol
                        # Invoke callback
                        if self.on_data:
                            print(f"[RECEIVE] Calling on_data callback")
                            self.on_data(text)
                        else:
                            print(f"[RECEIVE] WARNING: on_data callback not set!")

                    # Process GMCP data
                    for module, data in gmcp_list:
                        if self.on_gmcp:
                            print(f"[RECEIVE] GMCP: {module}")
                            self.on_gmcp(module, data)

                except socket.timeout:
                    # Timeout, continue
                    print(f"[RECEIVE] Timeout, waiting...")
                    continue
                except Exception as e:
                    # Error in receive, disconnect
                    print(f"[RECEIVE] Error: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    self._set_state(ConnectionState.ERROR, f"Error recibiendo: {str(e)}")
                    break

        except Exception as e:
            print(f"[RECEIVE] Loop error: {str(e)}")
            import traceback
            traceback.print_exc()
            self._set_state(ConnectionState.ERROR, f"Error en receive loop: {str(e)}")
        finally:
            print(f"[RECEIVE] Loop ended")
            self.running = False
            if self.socket:
                try:
                    self.socket.close()
                except Exception:
                    pass
                self.socket = None

    def _send_raw(self, data: bytes):
        """Internal callback for Telnet protocol to send responses."""
        self.send_raw(data)

    def _set_state(self, state: ConnectionState, message: str):
        """Update connection state and invoke callback."""
        self.state = state
        if self.on_state:
            self.on_state(state, message)

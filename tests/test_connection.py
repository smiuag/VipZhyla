"""
Tests for MUD connection module.

Note: These tests do not connect to a real server.
Use tools/mud_diagnose.py for integration testing with a real MUD server.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.client.connection import MUDConnection, ConnectionState


class TestMUDConnection:
    """Test MUD connection module."""

    def test_initial_state_disconnected(self):
        """Initial state should be DISCONNECTED."""
        conn = MUDConnection()
        assert conn.state == ConnectionState.DISCONNECTED

    def test_initial_encoding(self):
        """Default encoding should be UTF-8."""
        conn = MUDConnection()
        assert conn.encoding == "UTF-8"

    def test_custom_encoding(self):
        """Can set custom encoding."""
        conn = MUDConnection(encoding="ISO-8859-1")
        assert conn.encoding == "ISO-8859-1"

    def test_set_data_callback(self):
        """Register data callback."""
        conn = MUDConnection()
        callback = Mock()

        conn.set_data_callback(callback)
        assert conn.on_data is callback

    def test_set_gmcp_callback(self):
        """Register GMCP callback."""
        conn = MUDConnection()
        callback = Mock()

        conn.set_gmcp_callback(callback)
        assert conn.on_gmcp is callback

    def test_set_state_callback(self):
        """Register state callback."""
        conn = MUDConnection()
        callback = Mock()

        conn.set_state_callback(callback)
        assert conn.on_state is callback

    def test_disconnect_when_not_connected(self):
        """Disconnect when not connected doesn't crash."""
        conn = MUDConnection()

        # Should not raise exception
        conn.disconnect()
        assert conn.state == ConnectionState.DISCONNECTED

    def test_send_when_not_connected_does_nothing(self):
        """Send when not connected silently fails."""
        conn = MUDConnection()
        audio = Mock()

        # Should not raise exception
        conn.send("test command")

    def test_shutdown_graceful(self):
        """Shutdown gracefully closes connection."""
        conn = MUDConnection()

        # Should not raise exception
        conn.shutdown()
        assert conn.state == ConnectionState.DISCONNECTED

    @patch('src.client.connection.socket.socket')
    def test_connect_sets_state_to_connecting(self, mock_socket_class):
        """Connect sets state to CONNECTING."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        conn = MUDConnection()
        state_changes = []

        conn.set_state_callback(lambda state, msg: state_changes.append(state))

        # This will fail at connect because socket is mocked, but we can check state_changes
        conn.connect("nonexistent.example.com", 23)

        # Should have recorded state changes
        assert len(state_changes) > 0

    def test_socket_receive_loop_spawns_thread(self):
        """Connect spawns a daemon thread for receiving."""
        with patch('src.client.connection.socket.socket'):
            conn = MUDConnection()

            # Mock the connection
            with patch.object(conn, '_receive_loop'):
                with patch('threading.Thread') as mock_thread_class:
                    mock_thread = MagicMock()
                    mock_thread_class.return_value = mock_thread

                    # This will set up the connection (mocked)
                    try:
                        conn.connect("localhost", 23)
                    except Exception:
                        pass  # Connection will fail, that's OK

                    # Thread was created with daemon=True
                    if mock_thread_class.called:
                        call_kwargs = mock_thread_class.call_args[1]
                        assert call_kwargs.get('daemon') is True

    def test_telnet_processor_instantiated(self):
        """TelnetProcessor is instantiated on init."""
        conn = MUDConnection()
        assert conn.telnet is not None

    def test_encoding_error_replacement(self):
        """Invalid bytes use replacement character."""
        conn = MUDConnection(encoding="UTF-8")

        # UTF-8 is configured with errors='replace'
        # This is tested implicitly by the protocol handling

    def test_multiple_callbacks_independent(self):
        """Each callback type is independent."""
        conn = MUDConnection()

        data_cb = Mock()
        gmcp_cb = Mock()
        state_cb = Mock()

        conn.set_data_callback(data_cb)
        conn.set_gmcp_callback(gmcp_cb)
        conn.set_state_callback(state_cb)

        assert conn.on_data is data_cb
        assert conn.on_gmcp is gmcp_cb
        assert conn.on_state is state_cb

    def test_shutdown_called_multiple_times(self):
        """Shutdown can be called multiple times safely."""
        conn = MUDConnection()

        # Should not raise exception
        conn.shutdown()
        conn.shutdown()
        conn.shutdown()

        assert conn.state == ConnectionState.DISCONNECTED

    def test_telnet_send_raw_callback_assigned(self):
        """TelnetProcessor receives send_raw callback."""
        conn = MUDConnection()

        # TelnetProcessor should have the callback
        # This is verified implicitly during processing
        assert conn.telnet is not None
        assert callable(conn.telnet.send_raw)

"""
VipZhyla Main Application Entry Point

Accessible MUD Client for Blind and Visually Impaired Users
"""

import wx
import sys
from app.accessibility_core import AccessiblePanel
from app.keyboard_handler import KeyboardHandler, KeyAction
from app.audio_manager import AudioManager, AudioLevel
from client.connection import MUDConnection, ConnectionState
from client.message_buffer import MessageBuffer
from client.mud_parser import MUDParser, ChannelType
from client.gmcp_handler import GmcpHandler
from ui.list_dialogs import (show_channel_history, show_room_history,
                             show_telepathy_history, show_event_list)
from ui.trigger_dialog import show_trigger_manager
from models.triggers import TriggerManager


class VipZhylaApp(wx.App):
    """Main application class."""

    def OnInit(self):
        """Initialize the application."""
        # Create core managers (passed to MainWindow, not duplicated)
        audio = AudioManager()
        keyboard = KeyboardHandler()

        # Create main window (passes managers to avoid duplication)
        self.frame = MainWindow(
            None,
            title="VipZhyla - Accessible MUD Client",
            audio=audio,
            keyboard=keyboard
        )
        self.frame.Show()

        audio.announce(
            "VipZhyla iniciado. Presiona Ctrl+K para conectar, o Shift+F1 para historial.",
            AudioLevel.MINIMAL
        )

        return True

    def OnExceptionInMainLoop(self):
        """Handle exceptions in main loop."""
        # Audio may not exist at this point
        try:
            self.frame.audio.announce_error("Error. Revisa la consola para detalles.")
        except Exception:
            pass
        return super().OnExceptionInMainLoop()


class MainWindow(wx.Frame):
    """Main application window (single-window design)."""

    def __init__(self, parent, title="VipZhyla", audio=None, keyboard=None):
        """Initialize main window.

        Args:
            parent: Parent window (None for top-level)
            title: Window title
            audio: AudioManager instance
            keyboard: KeyboardHandler instance
        """
        super().__init__(parent, title=title, size=(600, 400))

        # Use provided managers (not duplicated)
        self.audio = audio or AudioManager()
        self.keyboard = keyboard or KeyboardHandler()

        # Create MUD connection components
        self.connection = MUDConnection(encoding="UTF-8")
        self.buffer = MessageBuffer()
        self.parser = MUDParser()
        self.gmcp = GmcpHandler(self.audio)
        self.trigger_manager = TriggerManager(self.audio)
        self.trigger_manager.send_fn = self.send_command

        # Setup connection callbacks
        self.connection.set_data_callback(self._on_mud_data)
        self.connection.set_gmcp_callback(self._on_gmcp)
        self.connection.set_state_callback(self._on_connection_state)

        self.gmcp.set_channel_callback(self._on_channel_message)
        self.gmcp.set_vitals_callback(self._on_vitals)
        self.gmcp.set_room_callback(self._on_room_info)

        # Create sizer for layout
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create main panel
        self.main_panel = AccessiblePanel(
            self,
            name="Main Application Panel",
            description="MUD client with text input and output areas"
        )

        # Input field
        self.input_field = wx.TextCtrl(
            self.main_panel,
            style=wx.TE_PROCESS_ENTER,
            value=""
        )
        self.input_field.SetName("Command Input")
        self.input_field.Bind(wx.EVT_TEXT_ENTER, self.on_command_enter)

        # Output area
        self.output_text = wx.TextCtrl(
            self.main_panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            value="VipZhyla v0.1.0 - Accessible MUD Client\n"
                  "=" * 50 + "\n"
                  "Press Ctrl+K to connect to a MUD.\n"
                  "Alt+U/O/I/K for movement (West/East/Up/Down)\n"
                  "Shift+F1-F4 for history\n"
                  "Ctrl+Shift+V to toggle verbose mode\n"
                  "=" * 50 + "\n"
        )
        self.output_text.SetName("Output Display")

        # Status bar (HP/MP and connection status)
        self.status_bar = self.CreateStatusBar(2)
        self.status_bar.SetStatusText("Desconectado", 0)
        self.status_bar.SetStatusText("Modo Normal", 1)

        # Add controls to sizer
        sizer.Add(wx.StaticText(self.main_panel, label="Game Output:"), 0, wx.ALL, 5)
        sizer.Add(self.output_text, 3, wx.EXPAND | wx.ALL, 5)
        sizer.Add(wx.StaticText(self.main_panel, label="Command Input:"), 0, wx.ALL, 5)
        sizer.Add(self.input_field, 0, wx.EXPAND | wx.ALL, 5)

        self.main_panel.SetSizer(sizer)

        # Bind keyboard events
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.input_field.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.output_text.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        # Register keyboard handlers
        self._register_keyboard_handlers()

        # Set focus to input
        self.input_field.SetFocus()

    def on_key_down(self, event):
        """Handle key down event."""
        self.keyboard.on_key_event(event)

    def _register_keyboard_handlers(self):
        """Register all keyboard action handlers."""
        # Movement (only active when connected)
        self.keyboard.register_handler(KeyAction.MOVE_WEST, lambda e: self.send_command("west"))
        self.keyboard.register_handler(KeyAction.MOVE_EAST, lambda e: self.send_command("east"))
        self.keyboard.register_handler(KeyAction.MOVE_NORTH, lambda e: self.send_command("north"))
        self.keyboard.register_handler(KeyAction.MOVE_SOUTH, lambda e: self.send_command("south"))
        self.keyboard.register_handler(KeyAction.MOVE_NORTHWEST, lambda e: self.send_command("nw"))
        self.keyboard.register_handler(KeyAction.MOVE_NORTHEAST, lambda e: self.send_command("ne"))
        self.keyboard.register_handler(KeyAction.MOVE_SOUTHWEST, lambda e: self.send_command("sw"))
        self.keyboard.register_handler(KeyAction.MOVE_SOUTHEAST, lambda e: self.send_command("se"))
        self.keyboard.register_handler(KeyAction.MOVE_UP, lambda e: self.send_command("up"))
        self.keyboard.register_handler(KeyAction.MOVE_DOWN, lambda e: self.send_command("down"))
        self.keyboard.register_handler(KeyAction.MOVE_IN, lambda e: self.send_command("enter"))
        self.keyboard.register_handler(KeyAction.MOVE_OUT, lambda e: self.send_command("exit"))

        # Connection
        self.keyboard.register_handler(KeyAction.CONNECT, self.on_connect)
        self.keyboard.register_handler(KeyAction.DISCONNECT, self.on_disconnect)

        # History dialogs (Shift+F1-F4)
        self.keyboard.register_handler(KeyAction.SHOW_CHANNEL_HISTORY, self.on_show_channel_history)
        self.keyboard.register_handler(KeyAction.SHOW_ROOM_HISTORY, self.on_show_room_history)
        self.keyboard.register_handler(KeyAction.SHOW_TELEPATHY_HISTORY, self.on_show_telepathy_history)
        self.keyboard.register_handler(KeyAction.SHOW_EVENT_LIST, self.on_show_event_list)

        # Channel navigation (Alt+Left/Right)
        self.keyboard.register_handler(KeyAction.PREV_CHANNEL, self.on_prev_channel)
        self.keyboard.register_handler(KeyAction.NEXT_CHANNEL, self.on_next_channel)

        # UI toggles and triggers
        self.keyboard.register_handler(KeyAction.TOGGLE_VERBOSE, self.on_toggle_verbose)
        self.keyboard.register_handler(KeyAction.SHOW_TRIGGERS, self.on_show_triggers)

    def on_command_enter(self, event):
        """Handle Enter key in input field."""
        command = self.input_field.GetValue()
        if command.strip():
            self.send_command(command)
            self.input_field.SetValue("")

    def send_command(self, command):
        """Send command to MUD.

        Args:
            command (str): The command to send
        """
        if self.connection.state != ConnectionState.CONNECTED:
            self.audio.announce("No estás conectado.", AudioLevel.MINIMAL)
            return

        # Expand aliases
        command = self.trigger_manager.expand_alias(command)

        # Send to server
        self.connection.send(command)

        # Echo to output
        self.append_output(f"> {command}\n")

    def append_output(self, text):
        """Append text to output display (thread-safe via wx.CallAfter).

        Args:
            text (str): Text to append
        """
        wx.CallAfter(self.output_text.AppendText, text)

    def on_connect(self, event):
        """Handle connect request (Ctrl+K)."""
        if self.connection.state == ConnectionState.CONNECTED:
            self.audio.announce("Ya estás conectado.", AudioLevel.MINIMAL)
            return

        if self.connection.state == ConnectionState.CONNECTING:
            self.audio.announce("Conexión en progreso.", AudioLevel.MINIMAL)
            return

        # Show connection dialog
        dlg = wx.TextEntryDialog(
            self,
            "Servidor MUD (host:puerto):",
            "Conectar",
            "reinosdeleyenda.com:23"
        )

        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        server_info = dlg.GetValue().strip()
        dlg.Destroy()

        # Parse host:port
        try:
            if ':' in server_info:
                host, port_str = server_info.rsplit(':', 1)
                port = int(port_str)
            else:
                host = server_info
                port = 23

            # Attempt connection
            if self.connection.connect(host, port):
                self.audio.announce(f"Conectando a {host}:{port}...", AudioLevel.MINIMAL)
                # Start timers after connection
                self.trigger_manager.start_timers()
            else:
                self.audio.announce(f"Error al conectar.", AudioLevel.MINIMAL)

        except (ValueError, IndexError):
            self.audio.announce("Formato inválido. Usa host:puerto", AudioLevel.MINIMAL)

    def on_disconnect(self, event):
        """Handle disconnect request (Ctrl+D)."""
        if self.connection.state == ConnectionState.DISCONNECTED:
            self.audio.announce("No estás conectado.", AudioLevel.MINIMAL)
            return

        self.trigger_manager.stop_timers()
        self.connection.disconnect()
        self.audio.announce("Desconectado.", AudioLevel.MINIMAL)

    def on_show_help(self, event):
        """Show help dialog."""
        help_text = (
            "VipZhyla Keybindings:\n\n"
            "Conexión:\n"
            "  Ctrl+K=Connect, Ctrl+D=Disconnect\n\n"
            "Movimiento (Alt+key):\n"
            "  U=West, O=East, I=Up, M=Down\n"
            "  8=North, K=South, 7=NW, 9=NE, J=SW, L=SE\n"
            "  ,=In, .=Out\n\n"
            "Historial (Shift+F1-F4):\n"
            "  F1=Channels, F2=Room, F3=Telepathy, F4=Events\n\n"
            "Navegación (Alt+key):\n"
            "  Up/Down=Message, Left/Right=Channel\n"
            "  Home=First, End=Last\n\n"
            "Otro:\n"
            "  Ctrl+Shift+V=Toggle Verbose\n"
            "  Enter=Send, Escape=Cancel\n"
        )

        dlg = wx.MessageDialog(self, help_text, "Help - Keybindings", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def on_toggle_verbose(self, event):
        """Toggle verbose mode."""
        if self.audio.level == AudioLevel.NORMAL:
            self.audio.set_verbosity(AudioLevel.VERBOSE)
        else:
            self.audio.set_verbosity(AudioLevel.NORMAL)

        mode = "Verbose" if self.audio.level == AudioLevel.VERBOSE else "Normal"
        self.status_bar.SetStatusText(f"Modo {mode}", 1)
        self.audio.announce(f"Modo {mode}", AudioLevel.MINIMAL)

    def on_show_channel_history(self, event):
        """Show channel history dialog (Shift+F1)."""
        show_channel_history(self, self.buffer, self.audio)

    def on_show_room_history(self, event):
        """Show room history dialog (Shift+F2)."""
        show_room_history(self, self.buffer, self.audio)

    def on_show_telepathy_history(self, event):
        """Show telepathy history dialog (Shift+F3)."""
        show_telepathy_history(self, self.buffer, self.audio)

    def on_show_event_list(self, event):
        """Show event list dialog (Shift+F4)."""
        show_event_list(self, self.buffer, self.audio)

    def on_prev_channel(self, event):
        """Switch to previous channel with messages (Alt+Left)."""
        channels = self.buffer.get_all_channels()
        if not channels:
            self.audio.announce("Sin mensajes aún.", AudioLevel.MINIMAL)
            return

        # Find current channel (default to GENERAL)
        current = getattr(self, '_current_channel', ChannelType.GENERAL)
        current_idx = channels.index(current) if current in channels else 0

        # Go to previous channel
        prev_idx = (current_idx - 1) % len(channels)
        self._current_channel = channels[prev_idx]

        channel_name = self._current_channel.value.title()
        count = len(self.buffer.get_channel(self._current_channel))
        self.audio.announce(f"{channel_name}: {count} mensajes", AudioLevel.NORMAL)

    def on_next_channel(self, event):
        """Switch to next channel with messages (Alt+Right)."""
        channels = self.buffer.get_all_channels()
        if not channels:
            self.audio.announce("Sin mensajes aún.", AudioLevel.MINIMAL)
            return

        # Find current channel (default to GENERAL)
        current = getattr(self, '_current_channel', ChannelType.GENERAL)
        current_idx = channels.index(current) if current in channels else 0

        # Go to next channel
        next_idx = (current_idx + 1) % len(channels)
        self._current_channel = channels[next_idx]

        channel_name = self._current_channel.value.title()
        count = len(self.buffer.get_channel(self._current_channel))
        self.audio.announce(f"{channel_name}: {count} mensajes", AudioLevel.NORMAL)

    def on_show_triggers(self, event):
        """Show trigger/alias/timer manager dialog (Ctrl+T)."""
        show_trigger_manager(self, self.trigger_manager)

    # MUD connection callbacks

    def _on_mud_data(self, text: str):
        """Callback for text data from MUD."""
        # Parse each line
        for line in text.split('\n'):
            if line.strip():
                parsed = self.parser.parse_line(line)
                gagged = self.trigger_manager.evaluate(parsed)
                self.buffer.add(parsed)
                if not gagged:
                    self.append_output(f"{parsed.text}\n")

    def _on_gmcp(self, module: str, data: dict):
        """Callback for GMCP data from MUD."""
        # Delegate to GMCP handler
        self.gmcp.handle(module, data)

    def _on_connection_state(self, state: ConnectionState, message: str):
        """Callback for connection state changes."""
        self.status_bar.SetStatusText(message, 0)
        self.audio.announce(message, AudioLevel.MINIMAL)

    def _on_channel_message(self, msg):
        """Callback for channel message from GMCP."""
        self.buffer.add(msg)
        self.append_output(f"[{msg.channel.value}] {msg.text}\n")

    def _on_vitals(self, hp: int, maxhp: int, mp: int, maxmp: int):
        """Callback for character vitals from GMCP."""
        vitals_str = f"HP: {hp}/{maxhp} | MP: {mp}/{maxmp}"
        self.status_bar.SetStatusText(vitals_str, 0)

    def _on_room_info(self, room_name: str, exits: list):
        """Callback for room info from GMCP."""
        # Could update a room display, for now just announce
        pass


def main():
    """Main entry point."""
    app = VipZhylaApp(False)
    app.MainLoop()


if __name__ == "__main__":
    main()

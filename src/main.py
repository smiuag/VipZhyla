"""
VipZhyla Main Application Entry Point

Accessible MUD Client for Blind and Visually Impaired Users
"""

import wx
import sys
import re
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
from ui.help_dialog import show_help
from ui.preferences_dialog import PreferencesDialog
from models.triggers import TriggerManager
from models.map_service import MapService
from models.character_state import CharacterState
from models.channel_config import ChannelConfig
from client.character_parser import CharacterParser


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
            "VipZhyla iniciado. Presiona F1 para ayuda, Ctrl+K para conectar.",
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
        super().__init__(parent, title=title, size=(1000, 700))
        self.SetMinSize((800, 600))

        # Use provided managers (not duplicated)
        self.audio = audio or AudioManager()
        self.keyboard = keyboard or KeyboardHandler()

        # Create MUD connection components
        self.connection = MUDConnection(encoding="UTF-8")
        self.buffer = MessageBuffer()
        self.parser = MUDParser()
        self.gmcp = GmcpHandler(self.audio)
        self.character_state = CharacterState()  # Character state tracking
        self.channel_config = ChannelConfig()  # Channel muting configuration
        self.trigger_manager = TriggerManager(self.audio)
        self.trigger_manager.send_fn = self.send_command
        self.trigger_manager.character_state = self.character_state  # Pass state to triggers

        # Output filtering preferences
        self.filter_long_descriptions = True
        self.max_description_length = 250

        # Map service
        self.map_service = MapService()
        self.map_service.load("src/data/map-reinos.json")
        self._waiting_for_locate = False
        self._walk_steps: list[str] = []
        self._walk_index = 0

        # Setup connection callbacks
        self.connection.set_data_callback(self._on_mud_data)
        self.connection.set_gmcp_callback(self._on_gmcp)
        self.connection.set_state_callback(self._on_connection_state)

        self.gmcp.set_channel_callback(self._on_channel_message)
        self.gmcp.set_vitals_callback(self._on_vitals)
        self.gmcp.set_status_callback(self._on_status_changed)
        self.gmcp.set_room_callback(self._on_room_info)
        self.gmcp.set_room_actual_callback(self._on_room_actual)
        self.gmcp.set_room_movimiento_callback(self._on_room_movimiento)

        # Create main panel
        self.main_panel = AccessiblePanel(
            self,
            name="Main Application Panel",
            description="MUD client with text input and output areas"
        )
        self.main_panel.SetBackgroundColour(wx.Colour(240, 240, 245))

        # Create sizer for layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.SetMinSize((950, 650))

        # Fonts
        header_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        output_font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        input_font = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        # Output label
        output_label = wx.StaticText(self.main_panel, label="MUD Output:")
        output_label.SetFont(header_font)
        output_label.SetForegroundColour(wx.Colour(40, 40, 80))
        sizer.Add(output_label, 0, wx.LEFT | wx.TOP | wx.RIGHT, 12)

        # Output area
        self.output_text = wx.TextCtrl(
            self.main_panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            value="VipZhyla v0.1.0 - Accessible MUD Client\n"
                  "=" * 60 + "\n"
                  "Ctrl+K: Connect to MUD\n"
                  "Ctrl+P: Preferences (encoding, etc.)\n"
                  "Ctrl+S: Stop speech\n"
                  "Alt+U/O/I/K: Movement (West/East/Up/Down)\n"
                  "Alt+8/K/7/9: Movement (North/South/NW/NE)\n"
                  "Shift+F1-F4: History dialogs\n"
                  "Ctrl+T: Trigger Manager\n"
                  "Ctrl+Shift+V: Toggle verbose mode\n"
                  "F1: Help\n"
                  "=" * 60 + "\n"
        )
        self.output_text.SetFont(output_font)
        self.output_text.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.output_text.SetForegroundColour(wx.Colour(20, 20, 60))
        sizer.Add(self.output_text, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Input label
        input_label = wx.StaticText(self.main_panel, label="Command Input:")
        input_label.SetFont(header_font)
        input_label.SetForegroundColour(wx.Colour(40, 40, 80))
        sizer.Add(input_label, 0, wx.LEFT | wx.TOP | wx.RIGHT, 12)

        # Input field
        self.input_field = wx.TextCtrl(
            self.main_panel,
            style=wx.TE_PROCESS_ENTER,
            value=""
        )
        self.input_field.SetFont(input_font)
        self.input_field.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.input_field.SetForegroundColour(wx.Colour(0, 0, 0))
        self.input_field.SetMinSize((-1, 32))
        self.input_field.Bind(wx.EVT_TEXT_ENTER, self.on_command_enter)
        sizer.Add(self.input_field, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.main_panel.SetSizer(sizer)
        self.output_text.SetName("Output Display")

        # Status bar (HP/MP and connection status)
        self.status_bar = self.CreateStatusBar(2)
        self.status_bar.SetStatusText("Desconectado | Modo Normal", 0)
        status_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.status_bar.SetFont(status_font)

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
        self.keyboard.register_handler(KeyAction.MOVE_WEST, lambda e: self.send_command("oeste"))
        self.keyboard.register_handler(KeyAction.MOVE_EAST, lambda e: self.send_command("este"))
        self.keyboard.register_handler(KeyAction.MOVE_NORTH, lambda e: self.send_command("norte"))
        self.keyboard.register_handler(KeyAction.MOVE_SOUTH, lambda e: self.send_command("sur"))
        self.keyboard.register_handler(KeyAction.MOVE_NORTHWEST, lambda e: self.send_command("noroeste"))
        self.keyboard.register_handler(KeyAction.MOVE_NORTHEAST, lambda e: self.send_command("noreste"))
        self.keyboard.register_handler(KeyAction.MOVE_SOUTHWEST, lambda e: self.send_command("sudoeste"))
        self.keyboard.register_handler(KeyAction.MOVE_SOUTHEAST, lambda e: self.send_command("sudeste"))
        self.keyboard.register_handler(KeyAction.MOVE_UP, lambda e: self.send_command("arriba"))
        self.keyboard.register_handler(KeyAction.MOVE_DOWN, lambda e: self.send_command("abajo"))
        self.keyboard.register_handler(KeyAction.MOVE_IN, lambda e: self.send_command("entrar"))
        self.keyboard.register_handler(KeyAction.MOVE_OUT, lambda e: self.send_command("salir"))

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

        # UI toggles and management
        self.keyboard.register_handler(KeyAction.SHOW_HELP, self.on_show_help)
        self.keyboard.register_handler(KeyAction.SHOW_PREFERENCES, self.on_show_preferences)
        self.keyboard.register_handler(KeyAction.SHOW_TRIGGERS, self.on_show_triggers)
        self.keyboard.register_handler(KeyAction.TOGGLE_VERBOSE, self.on_toggle_verbose)
        self.keyboard.register_handler(KeyAction.STOP_SPEECH, lambda e: self.audio.stop())

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
        # Stop walk if in progress (user typed a command)
        if self._walk_steps:
            self._stop_walk()

        # Handle locate command (sends "ojear" to MUD)
        if command.strip().lower() == "locate":
            if self.connection.state != ConnectionState.CONNECTED:
                self.audio.announce("No estás conectado.", AudioLevel.MINIMAL)
                return
            self._waiting_for_locate = True
            self.connection.send("ojear")
            self.append_output(f"> {command}\n")
            return

        # Handle irsala command (client-side navigation)
        if command.lower().startswith("irsala "):
            self._handle_irsala(command[7:].strip())
            return

        # Handle parar command (stop walk)
        if command.strip().lower() == "parar":
            self.audio.announce("Detenido.", AudioLevel.MINIMAL)
            return

        # Normal MUD commands
        if self.connection.state != ConnectionState.CONNECTED:
            self.audio.announce("No estás conectado.", AudioLevel.MINIMAL)
            return

        # Expand aliases
        command = self.trigger_manager.expand_alias(command)

        # Send to server
        self.connection.send(command)

        # Echo to output
        self.append_output(f"> {command}\n")

    def append_output(self, text, channel=None):
        """Append text to output display (thread-safe via wx.CallAfter).

        Args:
            text (str): Text to append
            channel (ChannelType, optional): Channel the message came from (for muting)
        """
        wx.CallAfter(self.output_text.AppendText, text)
        # Announce MUD output to screen reader users (text-to-speech)
        # Only announce if connected (avoid spamming initial welcome message)
        if self.connection.state == ConnectionState.CONNECTED:
            # Check if channel is muted
            if channel and self.channel_config.is_muted(channel):
                return  # Don't announce muted channels

            # Apply output filtering (FiltroSalidas): don't announce very long descriptions
            should_announce = True
            if self.filter_long_descriptions and len(text.strip()) > self.max_description_length:
                should_announce = False

            if should_announce:
                wx.CallAfter(self.audio.announce, text.strip(), AudioLevel.NORMAL)

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
        """Show comprehensive help dialog."""
        show_help(self)

    def on_show_preferences(self, event):
        """Show preferences dialog."""
        dlg = PreferencesDialog(self, self.connection.encoding)
        if dlg.ShowModal() == wx.ID_OK:
            # Update encoding
            new_encoding = dlg.get_selected_encoding()
            if new_encoding.lower() != self.connection.encoding.lower():
                self.connection.set_encoding(new_encoding)
                self.audio.announce(f"Codificación: {new_encoding}", AudioLevel.MINIMAL)

            # Update output filtering preferences
            self.filter_long_descriptions = dlg.get_filter_long_descriptions()
            self.max_description_length = dlg.get_max_description_length()
            self.audio.announce(
                f"Filtrado: {'activado' if self.filter_long_descriptions else 'desactivado'}",
                AudioLevel.MINIMAL
            )
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
                # Check for locate response (line ending with [exits])
                if self._waiting_for_locate and re.search(r'\[.*?\]\s*$', line):
                    self._waiting_for_locate = False
                    room = self.map_service.find_room(line)
                    if room:
                        exits = ", ".join(room.e.keys())
                        self.audio.announce(f"Localizado: {room.n}. Salidas: {exits}", AudioLevel.MINIMAL)
                        self.map_service.set_current_room(room.id)
                    else:
                        self.audio.announce("No localizado. Sala ambigua o no encontrada.", AudioLevel.MINIMAL)

                parsed = self.parser.parse_line(line)
                gagged = self.trigger_manager.evaluate(parsed)
                self.buffer.add(parsed)
                if not gagged:
                    self.append_output(f"{parsed.text}\n", parsed.channel)

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
        self.append_output(f"[{msg.channel.value}] {msg.text}\n", msg.channel)

    def _on_vitals(self, hp: int, maxhp: int, mp: int, maxmp: int):
        """Callback for character vitals from GMCP."""
        # Update character state
        self.character_state.update_vitals(hp, maxhp, mp, maxmp)
        hp_pct = int((hp / maxhp * 100)) if maxhp > 0 else 0
        mp_pct = int((mp / maxmp * 100)) if maxmp > 0 else 0
        vitals_str = f"HP: {hp}/{maxhp} ({hp_pct}%) | MP: {mp}/{maxmp} ({mp_pct}%)"
        self.status_bar.SetStatusText(vitals_str, 0)

    def _on_status_changed(self, data: dict):
        """Callback for character status from GMCP Char.Status."""
        # Update character state with class, race, level, name
        CharacterParser.parse_gmcp_status(self.character_state, data)

    def _on_room_info(self, room_name: str, exits: list):
        """Callback for room info from GMCP."""
        # Could update a room display, for now just announce
        pass

    def _on_room_actual(self, name_line: str):
        """Callback for Room.Actual GMCP (room name with exits)."""
        # Resync only if already localized (avoid noise)
        if self.map_service.get_current_room() is not None:
            room = self.map_service.find_room(name_line)
            if room:
                self.map_service.set_current_room(room.id)

    def _on_room_movimiento(self, direction: str):
        """Callback for Room.Movimiento GMCP (direction taken)."""
        room = self.map_service.move_by_direction(direction)
        if room:
            exits = ", ".join(room.e.keys())
            self.audio.announce(f"{room.n}. Salidas: {exits}", AudioLevel.MINIMAL)

    def _handle_irsala(self, query: str):
        """Handle irsala (navigate to room) command."""
        if not self.map_service.get_current_room():
            self.audio.announce("No localizado. Escribe 'locate' primero.", AudioLevel.MINIMAL)
            return

        results = self.map_service.search_rooms(query)
        if not results:
            self.audio.announce(f"Sala no encontrada: {query}", AudioLevel.MINIMAL)
        elif len(results) == 1:
            self._walk_to(results[0])
        else:
            names = ", ".join(r.n for r in results[:5])
            count = len(results)
            suffix = "..." if count > 5 else ""
            self.audio.announce(f"{count} salas encontradas: {names}{suffix}", AudioLevel.MINIMAL)
            self.append_output(f"Varias salas encontradas:\n" + "\n".join(f"  {r.n}" for r in results) + "\n")

    def _walk_to(self, target):
        """Start walking to a target room."""
        current = self.map_service.get_current_room()
        if not current:
            self.audio.announce("No localizado.", AudioLevel.MINIMAL)
            return

        path = self.map_service.find_path(current.id, target.id)
        if path is None:
            self.audio.announce("Ruta no encontrada.", AudioLevel.MINIMAL)
            return

        self._walk_steps = path
        self._walk_index = 0
        self.audio.announce(f"Yendo a {target.n}. {len(path)} pasos.", AudioLevel.MINIMAL)
        self._walk_next_step()

    def _walk_next_step(self):
        """Send next step in walk sequence."""
        if self._walk_index >= len(self._walk_steps):
            self._walk_steps = []
            self._walk_index = 0
            return

        step = self._walk_steps[self._walk_index]
        self._walk_index += 1
        self.connection.send(step)
        wx.CallLater(1100, self._walk_next_step)

    def _stop_walk(self):
        """Stop current walk."""
        self._walk_steps = []
        self._walk_index = 0
        self.audio.announce("Viaje detenido.", AudioLevel.MINIMAL)


def main():
    """Main entry point."""
    app = VipZhylaApp(False)
    app.MainLoop()


if __name__ == "__main__":
    main()

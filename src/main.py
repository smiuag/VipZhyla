"""
VipZhyla Main Application Entry Point

Accessible MUD Client for Blind and Visually Impaired Users
"""

import wx
import sys
from app.accessibility_core import AccessiblePanel
from app.keyboard_handler import KeyboardHandler, KeyAction
from app.audio_manager import AudioManager, AudioLevel


class VipZhylaApp(wx.App):
    """Main application class."""

    def OnInit(self):
        """Initialize the application."""
        self.audio = AudioManager()
        self.keyboard = KeyboardHandler()

        # Create main window
        self.frame = MainWindow(None, title="VipZhyla - Accessible MUD Client")
        self.frame.Show()

        self.audio.announce(
            "VipZhyla started. Type Alt+O for options, Alt+H for help, or connect to a MUD.",
            AudioLevel.MINIMAL
        )

        return True

    def OnExceptionInMainLoop(self):
        """Handle exceptions in main loop."""
        self.audio.announce_error("An error occurred. Check the console for details.")
        return super().OnExceptionInMainLoop()


class MainWindow(wx.Frame):
    """Main application window (single-window design)."""

    def __init__(self, parent, title="VipZhyla"):
        """Initialize main window.

        Args:
            parent: Parent window (None for top-level)
            title: Window title
        """
        super().__init__(parent, title=title, size=(600, 400))

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
        self.input_field.SetDescription("Type MUD commands here")
        self.input_field.Bind(wx.EVT_TEXT_ENTER, self.on_command_enter)

        # Output area
        self.output_text = wx.TextCtrl(
            self.main_panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            value="VipZhyla v0.1.0 - Accessible MUD Client\n"
                  "=" * 50 + "\n"
                  "Welcome! Press Shift+F1 for channel history.\n"
                  "Alt+U/O/I/K for movement (West/East/Up/Down)\n"
                  "Press Alt+H for full keybinding list.\n"
                  "=" * 50 + "\n"
        )
        self.output_text.SetName("Output Display")
        self.output_text.SetDescription("Game text and messages appear here")

        # Status bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Ready | Verbose Mode")

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
        self.keyboard = KeyboardHandler()
        self.audio = AudioManager()
        self._register_keyboard_handlers()

        # Set focus to input
        self.input_field.SetFocus()

    def on_key_down(self, event):
        """Handle key down event."""
        self.keyboard.on_key_event(event)

    def _register_keyboard_handlers(self):
        """Register all keyboard action handlers."""
        # Movement
        self.keyboard.register_handler(KeyAction.MOVE_WEST, lambda e: self.send_command("west"))
        self.keyboard.register_handler(KeyAction.MOVE_EAST, lambda e: self.send_command("east"))
        self.keyboard.register_handler(KeyAction.MOVE_NORTH, lambda e: self.send_command("north"))
        self.keyboard.register_handler(KeyAction.MOVE_SOUTH, lambda e: self.send_command("south"))

        # History
        self.keyboard.register_handler(KeyAction.SHOW_CHANNEL_HISTORY, self.on_show_help)
        self.keyboard.register_handler(KeyAction.TOGGLE_VERBOSE, self.on_toggle_verbose)

    def on_command_enter(self, event):
        """Handle Enter key in input field."""
        command = self.input_field.GetValue()
        if command.strip():
            self.send_command(command)
            self.input_field.SetValue("")

    def send_command(self, command):
        """Send command to MUD (stub for now).

        Args:
            command (str): The command to send
        """
        self.append_output(f"> {command}\n")
        self.audio.announce(f"Sent: {command}", AudioLevel.VERBOSE)

    def append_output(self, text):
        """Append text to output display.

        Args:
            text (str): Text to append
        """
        self.output_text.AppendText(text)

    def on_show_help(self, event):
        """Show help dialog."""
        help_text = (
            "VipZhyla Keybindings:\n\n"
            "Movement (Alt+key):\n"
            "  U=West, O=East, I=Up, M=Down\n"
            "  8=North, K=South, 7=NW, 9=NE, J=SW, L=SE\n"
            "  ,=In, .=Out\n\n"
            "History (Shift+F1-F4):\n"
            "  F1=Channels, F2=Room, F3=Telepathy, F4=Events\n\n"
            "Navigation (Alt+key):\n"
            "  Up/Down=Message, Left/Right=Channel\n"
            "  Home=First, End=Last\n\n"
            "Other:\n"
            "  Ctrl+Shift+V=Toggle Verbose\n"
            "  Enter=Send Command, Escape=Cancel\n"
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
        self.status_bar.SetStatusText(f"Ready | {mode} Mode")


def main():
    """Main entry point."""
    app = VipZhylaApp(False)
    app.MainLoop()


if __name__ == "__main__":
    main()

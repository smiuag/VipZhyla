"""
Accessible help system for VipZhyla.

Main help dialog with tabs for different topics.
All content is user-facing, non-technical, and functional.
"""

import wx
from typing import Dict


class HelpDialog(wx.Dialog):
    """Main help dialog with tabbed content."""

    # Help content - KEEP THIS SYNCHRONIZED WITH README.md
    HELP_CONTENT = {
        "Start Here": (
            "WELCOME TO VIPZHYLA\n"
            "====================\n\n"
            "VipZhyla is a MUD (text adventure game) client designed for blind and "
            "visually impaired players. Everything is keyboard-based and works with "
            "screen readers like NVDA.\n\n"
            "Quick Start:\n"
            "1. Press Ctrl+K to connect to a MUD server\n"
            "2. Login with your character\n"
            "3. Use Alt+U/O/I/K to move (West/East/Up/Down)\n"
            "4. Press Shift+F1 to see recent messages\n\n"
            "For detailed help, use the tabs above."
        ),
        "Connection": (
            "CONNECTING TO A SERVER\n"
            "======================\n\n"
            "Press Ctrl+K to open the connection dialog.\n\n"
            "You'll be asked for:\n"
            "  Server: reinosdeleyenda.com:23\n"
            "  (Or any other MUD server)\n\n"
            "After connecting:\n"
            "  - You'll see the login prompt\n"
            "  - Type your username and password\n"
            "  - Follow the character selection menu\n\n"
            "To disconnect:\n"
            "  Press Ctrl+D\n\n"
            "Status: Check the bottom of the screen for connection status."
        ),
        "Movement": (
            "MOVING AROUND\n"
            "=============\n\n"
            "Use Alt+Key to move:\n"
            "  Alt+U = West\n"
            "  Alt+O = East\n"
            "  Alt+I = Up\n"
            "  Alt+M = Down\n"
            "  Alt+8 = North\n"
            "  Alt+K = South\n"
            "  Alt+7 = Northwest\n"
            "  Alt+9 = Northeast\n"
            "  Alt+J = Southwest\n"
            "  Alt+L = Southeast\n"
            "  Alt+, = Enter (building/portal)\n"
            "  Alt+. = Exit (go out)\n\n"
            "These keys are arranged like a numeric keypad for easy navigation."
        ),
        "Messages": (
            "READING MESSAGES\n"
            "================\n\n"
            "Message Channels:\n"
            "  Shift+F1 = All channels (Bando, Telepathy, etc.)\n"
            "  Shift+F2 = Room messages (what's happening around you)\n"
            "  Shift+F3 = Telepathy channel (private messages)\n"
            "  Shift+F4 = System messages (server events)\n\n"
            "Inside a message dialog:\n"
            "  Up/Down arrows = Read previous/next message\n"
            "  Page Up/Down = Jump 10 messages\n"
            "  Home/End = Jump to first/last message\n"
            "  Alt+Left/Right = Switch channels\n"
            "  Escape = Close dialog\n\n"
            "Your screen reader will announce your position as you navigate."
        ),
        "Typing": (
            "SENDING COMMANDS\n"
            "================\n\n"
            "The input field is at the bottom of the screen.\n"
            "Just type your command and press Enter.\n\n"
            "Examples:\n"
            "  look\n"
            "  examine potion\n"
            "  cast fireball orc\n"
            "  say Hello everyone!\n\n"
            "Your commands are echoed back so you know they were sent.\n\n"
            "Tip: Use Aliases to create shortcuts (see Aliases section)."
        ),
        "Triggers": (
            "TRIGGERS - REACT TO EVENTS\n"
            "===========================\n\n"
            "Triggers let you automatically react when something happens in the game.\n\n"
            "Example:\n"
            "  Pattern: 'You are poisoned'\n"
            "  Action: Announce 'Poison detected'\n"
            "  Result: When you're poisoned, you hear the announcement\n\n"
            "To manage triggers:\n"
            "  Press Ctrl+T to open Trigger Manager\n"
            "  Select 'Triggers' tab\n"
            "  Press 'New' to create one\n\n"
            "Trigger types:\n"
            "  - Normal: matches text anywhere in the line (case-insensitive)\n"
            "  - Regex: for advanced pattern matching\n\n"
            "Actions:\n"
            "  - Announce via speaker: Text-to-speech\n"
            "  - Hide line: Remove from screen (useful for spam)\n\n"
            "Enable/Disable: Toggle on/off without deleting"
        ),
        "Aliases": (
            "ALIASES - COMMAND SHORTCUTS\n"
            "============================\n\n"
            "Aliases let you create shortcuts for commands you type often.\n\n"
            "Example:\n"
            "  Shortcut: 'h'\n"
            "  Expands to: 'help'\n"
            "  When you type 'h' and press Enter, it sends 'help'\n\n"
            "With arguments:\n"
            "  Shortcut: 'e'\n"
            "  Expands to: 'examine'\n"
            "  Type 'e potion' → sends 'examine potion'\n\n"
            "To manage aliases:\n"
            "  Press Ctrl+T to open Trigger Manager\n"
            "  Select 'Aliases' tab\n"
            "  Press 'New' to create one\n\n"
            "Common aliases:\n"
            "  h → help\n"
            "  l → look\n"
            "  i → inventory\n"
            "  c → cast"
        ),
        "Timers": (
            "TIMERS - REPEAT ACTIONS\n"
            "=======================\n\n"
            "Timers let you do something automatically every N seconds.\n\n"
            "Example:\n"
            "  Every 30 seconds: Announce 'Time check'\n"
            "  Result: Every 30 seconds, you hear 'Time check'\n\n"
            "Common uses:\n"
            "  - Check your health regularly\n"
            "  - Announce to your group\n"
            "  - Remind yourself of a task\n\n"
            "To manage timers:\n"
            "  Press Ctrl+T to open Trigger Manager\n"
            "  Select 'Timers' tab\n"
            "  Press 'New' to create one\n\n"
            "Timers start when you connect and stop when you disconnect."
        ),
        "Settings": (
            "AUDIO & VERBOSITY\n"
            "=================\n\n"
            "Audio Output:\n"
            "  All announcements are spoken via your computer's speakers\n"
            "  Make sure your volume is turned up\n\n"
            "Verbosity (How much the app talks):\n"
            "  Press Ctrl+Shift+V to toggle between Normal and Verbose\n"
            "    Normal: Essential announcements only\n"
            "    Verbose: More detailed feedback\n\n"
            "Status Bar:\n"
            "  Bottom of screen shows:\n"
            "    Left: Connection status and health points\n"
            "    Right: Current mode (Normal/Verbose)"
        ),
        "Map": (
            "MAPA Y NAVEGACIÓN\n"
            "=================\n\n"
            "El mapa sigue tu posición automáticamente.\n\n"
            "Localización inicial:\n"
            "  Escribe 'locate' y pulsa Enter\n"
            "  El cliente envía 'ojear' al MUD y registra tu sala\n\n"
            "Tras localizar, el mapa te sigue:\n"
            "  Al moverte (norte, sur, etc.)\n"
            "  Al seguir a otro personaje (seguir Fulano)\n"
            "  El cliente anuncia la nueva sala y sus salidas\n\n"
            "Navegar a una sala:\n"
            "  Escribe 'irsala nombre' y pulsa Enter\n"
            "  Si hay una sola coincidencia, navega automáticamente\n"
            "  Si hay varias, te muestra las opciones\n"
            "  Escribe 'parar' para cancelar el viaje\n\n"
            "Ejemplos:\n"
            "  locate            → localiza tu posición actual\n"
            "  irsala mercado    → va al mercado más cercano\n"
            "  irsala plaza mayor → navega a la Plaza Mayor\n"
            "  parar             → cancela el viaje en curso\n\n"
            "Nota: Escribe 'locate' siempre que cambies de zona."
        ),
        "Keyboard Map": (
            "COMPLETE KEYBOARD REFERENCE\n"
            "===========================\n\n"
            "CONNECTION:\n"
            "  Ctrl+K = Connect to server\n"
            "  Ctrl+D = Disconnect\n\n"
            "MOVEMENT (Alt+Key):\n"
            "  U=West, O=East, I=Up, M=Down\n"
            "  8=North, K=South, 7=NW, 9=NE, J=SW, L=SE\n"
            "  ,=Enter, .=Exit\n\n"
            "MESSAGES:\n"
            "  Shift+F1 = All channels\n"
            "  Shift+F2 = Room history\n"
            "  Shift+F3 = Telepathy history\n"
            "  Shift+F4 = System messages\n"
            "  Alt+Left/Right = Switch channels\n"
            "  Alt+Up/Down = Previous/next message\n"
            "  Alt+Home/End = First/last message\n\n"
            "MANAGEMENT:\n"
            "  Ctrl+T = Triggers/Aliases/Timers\n"
            "  Ctrl+Shift+V = Toggle Verbose\n"
            "  Enter = Send command\n"
            "  Escape = Close dialog\n\n"
            "NAVIGATION:\n"
            "  locate = Localize your position\n"
            "  irsala <name> = Navigate to room\n"
            "  parar = Stop current walk"
        ),
    }

    def __init__(self, parent):
        """Initialize help dialog.

        Args:
            parent: Parent window
        """
        wx.Dialog.__init__(self, parent, title="VipZhyla Help",
                          style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self._build_ui()
        self.SetSize(700, 500)
        self.CentreOnParent()

    def _build_ui(self):
        """Build help dialog UI with notebook tabs."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create notebook
        notebook = wx.Notebook(self)

        # Add tabs for each help section
        for title, content in self.HELP_CONTENT.items():
            panel = self._create_help_panel(notebook, content)
            notebook.AddPage(panel, title)

        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 5)

        # Close button
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer()
        close_btn = wx.Button(self, wx.ID_CLOSE, "&Close")
        button_sizer.Add(close_btn, 0, wx.LEFT, 5)

        sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

        # Bind close
        self.Bind(wx.EVT_BUTTON, self.on_close, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def _create_help_panel(self, parent, content: str) -> wx.Panel:
        """Create a help panel with text content.

        Args:
            parent: Parent notebook
            content: Help text

        Returns:
            wx.Panel with text
        """
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Text control (read-only)
        text_ctrl = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            value=content
        )
        text_ctrl.SetName("Help Content")
        sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)
        return panel

    def on_key_down(self, event):
        """Handle keyboard events."""
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CLOSE)
        else:
            event.Skip()

    def on_close(self, event):
        """Close dialog."""
        self.EndModal(wx.ID_CLOSE)


def show_help(parent) -> None:
    """Show help dialog.

    Args:
        parent: Parent window
    """
    dlg = HelpDialog(parent)
    dlg.ShowModal()
    dlg.Destroy()

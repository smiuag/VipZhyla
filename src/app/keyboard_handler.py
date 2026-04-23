"""
Keyboard Handler - wxPython keyboard event processor

Handles all keyboard navigation and shortcuts for the application.
Keybindings are inspired by WCAG/ChannelHistory with VipMud movement keys.
"""

import wx
from enum import Enum


class KeyAction(Enum):
    """Enumeration of keyboard actions."""

    # Movement (VipMud-inspired QWERTY-based)
    MOVE_WEST = "move_west"      # Alt+U
    MOVE_EAST = "move_east"      # Alt+O
    MOVE_NORTH = "move_north"    # Alt+8
    MOVE_SOUTH = "move_south"    # Alt+K
    MOVE_NORTHWEST = "move_nw"   # Alt+7
    MOVE_NORTHEAST = "move_ne"   # Alt+9
    MOVE_SOUTHWEST = "move_sw"   # Alt+J
    MOVE_SOUTHEAST = "move_se"   # Alt+L
    MOVE_UP = "move_up"          # Alt+I
    MOVE_DOWN = "move_down"      # Alt+M
    MOVE_IN = "move_in"          # Alt+,
    MOVE_OUT = "move_out"        # Alt+.

    # Communication/History (Shift+F1-F4)
    SHOW_CHANNEL_HISTORY = "show_channel_history"      # Shift+F1
    SHOW_ROOM_HISTORY = "show_room_history"            # Shift+F2
    SHOW_TELEPATHY_HISTORY = "show_telepathy_history"  # Shift+F3
    SHOW_EVENT_LIST = "show_event_list"                # Shift+F4

    # Navigation within history
    NEXT_MESSAGE = "next_message"      # Alt+Down
    PREV_MESSAGE = "prev_message"      # Alt+Up
    FIRST_MESSAGE = "first_message"    # Alt+Home
    LAST_MESSAGE = "last_message"      # Alt+End
    NEXT_CHANNEL = "next_channel"      # Alt+Right
    PREV_CHANNEL = "prev_channel"      # Alt+Left

    # Global commands
    SEND_COMMAND = "send_command"      # Enter
    CANCEL = "cancel"                  # Escape
    COPY_TO_CLIPBOARD = "copy_clipboard"  # Ctrl+C

    # Connection
    CONNECT = "connect"              # Ctrl+K
    DISCONNECT = "disconnect"        # Ctrl+D

    # UI toggles
    TOGGLE_VERBOSE = "toggle_verbose"  # Ctrl+Shift+V
    SHOW_TRIGGERS = "show_triggers"    # Ctrl+T
    SHOW_HELP = "show_help"            # F1


class KeyboardHandler:
    """Handle keyboard input and route to appropriate handlers."""

    def __init__(self):
        """Initialize keyboard handler."""
        self.key_map = self._build_key_map()
        self.handlers = {}

    def _build_key_map(self):
        """Build mapping from wxPython key codes to actions.

        Returns:
            dict: Mapping of (key_code, modifiers) -> KeyAction
        """
        key_map = {}

        # Movement keys (Alt+QWERTY-based)
        key_map[(ord('U'), wx.MOD_ALT)] = KeyAction.MOVE_WEST
        key_map[(ord('O'), wx.MOD_ALT)] = KeyAction.MOVE_EAST
        key_map[(ord('8'), wx.MOD_ALT)] = KeyAction.MOVE_NORTH
        key_map[(ord('K'), wx.MOD_ALT)] = KeyAction.MOVE_SOUTH
        key_map[(ord('7'), wx.MOD_ALT)] = KeyAction.MOVE_NORTHWEST
        key_map[(ord('9'), wx.MOD_ALT)] = KeyAction.MOVE_NORTHEAST
        key_map[(ord('J'), wx.MOD_ALT)] = KeyAction.MOVE_SOUTHWEST
        key_map[(ord('L'), wx.MOD_ALT)] = KeyAction.MOVE_SOUTHEAST
        key_map[(ord('I'), wx.MOD_ALT)] = KeyAction.MOVE_UP
        key_map[(ord('M'), wx.MOD_ALT)] = KeyAction.MOVE_DOWN
        key_map[(ord(','), wx.MOD_ALT)] = KeyAction.MOVE_IN
        key_map[(ord('.'), wx.MOD_ALT)] = KeyAction.MOVE_OUT

        # Navigation keys
        key_map[(wx.WXK_DOWN, wx.MOD_ALT)] = KeyAction.NEXT_MESSAGE
        key_map[(wx.WXK_UP, wx.MOD_ALT)] = KeyAction.PREV_MESSAGE
        key_map[(wx.WXK_HOME, wx.MOD_ALT)] = KeyAction.FIRST_MESSAGE
        key_map[(wx.WXK_END, wx.MOD_ALT)] = KeyAction.LAST_MESSAGE
        key_map[(wx.WXK_RIGHT, wx.MOD_ALT)] = KeyAction.NEXT_CHANNEL
        key_map[(wx.WXK_LEFT, wx.MOD_ALT)] = KeyAction.PREV_CHANNEL

        # Help and history keys
        key_map[(wx.WXK_F1, 0)] = KeyAction.SHOW_HELP
        key_map[(wx.WXK_F1, wx.MOD_SHIFT)] = KeyAction.SHOW_CHANNEL_HISTORY
        key_map[(wx.WXK_F2, wx.MOD_SHIFT)] = KeyAction.SHOW_ROOM_HISTORY
        key_map[(wx.WXK_F3, wx.MOD_SHIFT)] = KeyAction.SHOW_TELEPATHY_HISTORY
        key_map[(wx.WXK_F4, wx.MOD_SHIFT)] = KeyAction.SHOW_EVENT_LIST

        # Global commands
        key_map[(wx.WXK_RETURN, 0)] = KeyAction.SEND_COMMAND
        key_map[(wx.WXK_ESCAPE, 0)] = KeyAction.CANCEL
        key_map[(ord('C'), wx.MOD_CONTROL)] = KeyAction.COPY_TO_CLIPBOARD
        key_map[(ord('K'), wx.MOD_CONTROL)] = KeyAction.CONNECT
        key_map[(ord('D'), wx.MOD_CONTROL)] = KeyAction.DISCONNECT
        key_map[(ord('T'), wx.MOD_CONTROL)] = KeyAction.SHOW_TRIGGERS
        key_map[(ord('V'), wx.MOD_CONTROL | wx.MOD_SHIFT)] = KeyAction.TOGGLE_VERBOSE

        return key_map

    def register_handler(self, action, callback):
        """Register callback for keyboard action.

        Args:
            action (KeyAction): The action to handle
            callback (callable): Function to call when action is triggered
        """
        self.handlers[action] = callback

    def on_key_event(self, event):
        """Handle wxPython key event.

        Args:
            event (wx.KeyEvent): The keyboard event
        """
        key_code = event.GetKeyCode()
        modifiers = event.GetModifiers()

        # Try exact match first
        action = self.key_map.get((key_code, modifiers))

        if action and action in self.handlers:
            self.handlers[action](event)
            event.Skip(False)  # Consume event
        else:
            event.Skip(True)  # Let default handler process it

    def get_key_description(self, action):
        """Get human-readable description of keyboard action.

        Args:
            action (KeyAction): The action to describe

        Returns:
            str: Description (e.g., "Alt+U for West")
        """
        descriptions = {
            KeyAction.MOVE_WEST: "Alt+U - Move West",
            KeyAction.MOVE_EAST: "Alt+O - Move East",
            KeyAction.MOVE_NORTH: "Alt+8 - Move North",
            KeyAction.MOVE_SOUTH: "Alt+K - Move South",
            KeyAction.MOVE_NORTHWEST: "Alt+7 - Move Northwest",
            KeyAction.MOVE_NORTHEAST: "Alt+9 - Move Northeast",
            KeyAction.MOVE_SOUTHWEST: "Alt+J - Move Southwest",
            KeyAction.MOVE_SOUTHEAST: "Alt+L - Move Southeast",
            KeyAction.MOVE_UP: "Alt+I - Move Up",
            KeyAction.MOVE_DOWN: "Alt+M - Move Down",
            KeyAction.MOVE_IN: "Alt+, - Move In",
            KeyAction.MOVE_OUT: "Alt+. - Move Out",
            KeyAction.SHOW_HELP: "F1 - Show Help",
            KeyAction.SHOW_CHANNEL_HISTORY: "Shift+F1 - Show Channel History",
            KeyAction.SHOW_ROOM_HISTORY: "Shift+F2 - Show Room History",
            KeyAction.SHOW_TELEPATHY_HISTORY: "Shift+F3 - Show Telepathy History",
            KeyAction.SHOW_EVENT_LIST: "Shift+F4 - Show Event List",
            KeyAction.NEXT_MESSAGE: "Alt+Down - Next Message",
            KeyAction.PREV_MESSAGE: "Alt+Up - Previous Message",
            KeyAction.FIRST_MESSAGE: "Alt+Home - First Message",
            KeyAction.LAST_MESSAGE: "Alt+End - Last Message",
            KeyAction.NEXT_CHANNEL: "Alt+Right - Next Channel",
            KeyAction.PREV_CHANNEL: "Alt+Left - Previous Channel",
            KeyAction.SEND_COMMAND: "Enter - Send Command",
            KeyAction.CANCEL: "Escape - Cancel",
            KeyAction.COPY_TO_CLIPBOARD: "Ctrl+C - Copy to Clipboard",
            KeyAction.CONNECT: "Ctrl+K - Connect to Server",
            KeyAction.DISCONNECT: "Ctrl+D - Disconnect from Server",
            KeyAction.SHOW_TRIGGERS: "Ctrl+T - Manage Triggers/Aliases/Timers",
            KeyAction.TOGGLE_VERBOSE: "Ctrl+Shift+V - Toggle Verbose Mode",
        }
        return descriptions.get(action, "Unknown action")

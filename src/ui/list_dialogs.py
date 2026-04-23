"""
History dialog windows for reviewing channel messages.

Provides accessible modal dialogs (Shift+F1-F4) for reviewing messages:
- Channel History: Multiple channels with Alt+Left/Right switcher
- Room History: GENERAL channel only
- Telepathy History: TELEPATHY channel only
- Event List: SYSTEM channel only

Uses wx.ListBox (natively accessible to screen readers).
Messages formatted as "HH:MM  text" with position announcements via TTS.
"""

import wx
from datetime import datetime
from typing import Optional, List
from client.mud_parser import ChannelType
from client.message_buffer import MessageBuffer, Message
from app.audio_manager import AudioManager, AudioLevel


class HistoryDialog(wx.Dialog):
    """Base dialog for viewing a single channel's message history.

    Features:
    - wx.ListBox for accessible message list (NVDA reads items on arrow navigation)
    - Status label showing "N / Total" message count
    - Up/Down arrows navigate, PgUp/PgDn jump 10 messages
    - Home/End jump to first/last message
    - Escape closes dialog
    - TTS announces position on each selection change
    """

    def __init__(self, parent, title: str, buffer: MessageBuffer,
                 channel: ChannelType, audio: Optional[AudioManager] = None):
        """Initialize history dialog.

        Args:
            parent: Parent window
            title: Dialog title
            buffer: MessageBuffer with message history
            channel: ChannelType to display
            audio: AudioManager for TTS announcements
        """
        wx.Dialog.__init__(self, parent, title=title,
                          style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.buffer = buffer
        self.channel = channel
        self.audio = audio
        self.messages: List[Message] = []

        self._build_ui()
        self._populate()
        self._select_last()

        # Bind events
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down, self)
        self.Bind(wx.EVT_LISTBOX, self._on_selection_changed)

    def _build_ui(self):
        """Build dialog UI: listbox + status label."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Listbox for messages
        self.message_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.message_list.SetName("Message List")
        sizer.Add(self.message_list, 1, wx.EXPAND | wx.ALL, 5)

        # Status bar showing position
        self.status_label = wx.StaticText(self, label="")
        sizer.Add(self.status_label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.SetSizer(sizer)
        self.SetSize(600, 400)
        self.CentreOnParent()

    def _populate(self):
        """Load messages from buffer for this channel."""
        self.messages = self.buffer.get_channel(self.channel)
        self.message_list.Clear()

        if not self.messages:
            self.message_list.Append("(No messages)")
            self.status_label.SetLabel("0 / 0")
            return

        for msg in self.messages:
            text = self._format_message(msg)
            self.message_list.Append(text)

        self.status_label.SetLabel(f"/ {len(self.messages)}")

    def _format_message(self, msg: Message) -> str:
        """Format message for display: "HH:MM  text"."""
        time_str = msg.timestamp.strftime("%H:%M") if msg.timestamp else "--:--"
        text = msg.text[:200] if msg.text else ""
        return f"{time_str}  {text}"

    def _select_last(self):
        """Select the last (newest) message."""
        if self.messages:
            self.message_list.SetSelection(len(self.messages) - 1)
            self._announce_position()

    def _announce_position(self):
        """Announce current position via TTS: 'Mensaje N de Total'."""
        if not self.messages:
            return

        sel = self.message_list.GetSelection()
        if sel >= 0:
            current = sel + 1  # 1-indexed for user
            total = len(self.messages)

            if self.audio:
                msg = f"Mensaje {current} de {total}"
                self.audio.announce(msg, AudioLevel.NORMAL)

            # Update status label
            self.status_label.SetLabel(f"{current} / {total}")

    def _on_selection_changed(self, event):
        """Announce position when listbox selection changes."""
        self._announce_position()

    def _on_key_down(self, event):
        """Handle keyboard navigation in dialog."""
        key_code = event.GetKeyCode()
        sel = self.message_list.GetSelection()

        if sel < 0:
            event.Skip()
            return

        if key_code == wx.WXK_ESCAPE:
            # Close dialog
            self.EndModal(wx.ID_CANCEL)
        elif key_code == wx.WXK_UP:
            # Previous message
            if sel > 0:
                self.message_list.SetSelection(sel - 1)
        elif key_code == wx.WXK_DOWN:
            # Next message
            if sel < len(self.messages) - 1:
                self.message_list.SetSelection(sel + 1)
        elif key_code == wx.WXK_PAGEUP:
            # Jump back 10 messages
            new_sel = max(0, sel - 10)
            self.message_list.SetSelection(new_sel)
        elif key_code == wx.WXK_PAGEDOWN:
            # Jump forward 10 messages
            new_sel = min(len(self.messages) - 1, sel + 10)
            self.message_list.SetSelection(new_sel)
        elif key_code == wx.WXK_HOME:
            # Jump to first message
            self.message_list.SetSelection(0)
        elif key_code == wx.WXK_END:
            # Jump to last message
            self.message_list.SetSelection(len(self.messages) - 1)
        else:
            event.Skip()


class ChannelHistoryDialog(wx.Dialog):
    """Dialog for reviewing multiple communication channels with Alt+Left/Right switching.

    Shows BANDO, TELEPATHY, CITIZENSHIP, GROUP channels.
    Starts on BANDO if available, else first channel with messages.
    Alt+Left/Right switches between channels.
    """

    def __init__(self, parent, buffer: MessageBuffer,
                 audio: Optional[AudioManager] = None):
        """Initialize channel history dialog with multi-channel support.

        Args:
            parent: Parent window
            buffer: MessageBuffer with message history
            audio: AudioManager for TTS announcements
        """
        wx.Dialog.__init__(self, parent, title="Channel History",
                          style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.buffer = buffer
        self.audio = audio

        # Available communication channels (excluding GENERAL and SYSTEM)
        self.comm_channels = [
            ChannelType.BANDO,
            ChannelType.TELEPATHY,
            ChannelType.CITIZENSHIP,
            ChannelType.GROUP,
        ]

        # Filter to channels with messages
        self.available_channels = [
            ch for ch in self.comm_channels
            if self.buffer.get_channel(ch)
        ]

        if not self.available_channels:
            # Fallback: show BANDO anyway (might be empty)
            self.available_channels = [ChannelType.BANDO]

        self.channel_idx = 0  # Start on first available channel
        self.messages: List[Message] = []

        self._build_ui()
        self._populate_for_channel()
        self._select_last()

        # Bind events
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down, self)
        self.Bind(wx.EVT_LISTBOX, self._on_selection_changed)

    def _build_ui(self):
        """Build dialog UI: listbox + channel/status labels."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Channel label
        self.channel_label = wx.StaticText(self, label="")
        font = self.channel_label.GetFont()
        font.MakeBold()
        self.channel_label.SetFont(font)
        sizer.Add(self.channel_label, 0, wx.LEFT | wx.TOP, 5)

        # Listbox for messages
        self.message_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.message_list.SetName("Message List")
        sizer.Add(self.message_list, 1, wx.EXPAND | wx.ALL, 5)

        # Status bar showing position
        self.status_label = wx.StaticText(self, label="")
        sizer.Add(self.status_label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.SetSizer(sizer)
        self.SetSize(600, 400)
        self.CentreOnParent()

    def _populate_for_channel(self):
        """Load messages for current channel."""
        channel = self.available_channels[self.channel_idx]
        self.messages = self.buffer.get_channel(channel)

        self.message_list.Clear()

        if not self.messages:
            self.message_list.Append("(No messages)")
            self.status_label.SetLabel("0 / 0")
        else:
            for msg in self.messages:
                text = self._format_message(msg)
                self.message_list.Append(text)

            self.status_label.SetLabel(f"/ {len(self.messages)}")

        # Update channel label
        channel = self.available_channels[self.channel_idx]
        channel_name = channel.value.title()
        self.channel_label.SetLabel(f"Channel: {channel_name}")

        # Announce channel change
        if self.audio:
            msg = f"{channel_name}: {len(self.messages)} mensajes"
            self.audio.announce(msg, AudioLevel.NORMAL)

    def _format_message(self, msg: Message) -> str:
        """Format message for display."""
        time_str = msg.timestamp.strftime("%H:%M") if msg.timestamp else "--:--"
        text = msg.text[:200] if msg.text else ""
        return f"{time_str}  {text}"

    def _select_last(self):
        """Select the last (newest) message."""
        if self.messages:
            self.message_list.SetSelection(len(self.messages) - 1)
            self._announce_position()

    def _announce_position(self):
        """Announce current message position."""
        if not self.messages:
            return

        sel = self.message_list.GetSelection()
        if sel >= 0:
            current = sel + 1
            total = len(self.messages)

            if self.audio:
                msg = f"Mensaje {current} de {total}"
                self.audio.announce(msg, AudioLevel.NORMAL)

            self.status_label.SetLabel(f"{current} / {total}")

    def _on_selection_changed(self, event):
        """Announce position when listbox selection changes."""
        self._announce_position()

    def _on_key_down(self, event):
        """Handle keyboard: arrows to navigate, Alt+Left/Right to switch channels."""
        key_code = event.GetKeyCode()
        modifiers = event.GetModifiers()
        sel = self.message_list.GetSelection()

        # Alt+Left/Right: switch channels
        if modifiers == wx.MOD_ALT:
            if key_code == wx.WXK_LEFT:
                # Previous channel
                if self.channel_idx > 0:
                    self.channel_idx -= 1
                    self._populate_for_channel()
                    self._select_last()
            elif key_code == wx.WXK_RIGHT:
                # Next channel
                if self.channel_idx < len(self.available_channels) - 1:
                    self.channel_idx += 1
                    self._populate_for_channel()
                    self._select_last()
            else:
                event.Skip()
        elif key_code == wx.WXK_ESCAPE:
            # Close dialog
            self.EndModal(wx.ID_CANCEL)
        elif sel >= 0:
            if key_code == wx.WXK_UP:
                if sel > 0:
                    self.message_list.SetSelection(sel - 1)
            elif key_code == wx.WXK_DOWN:
                if sel < len(self.messages) - 1:
                    self.message_list.SetSelection(sel + 1)
            elif key_code == wx.WXK_PAGEUP:
                new_sel = max(0, sel - 10)
                self.message_list.SetSelection(new_sel)
            elif key_code == wx.WXK_PAGEDOWN:
                new_sel = min(len(self.messages) - 1, sel + 10)
                self.message_list.SetSelection(new_sel)
            elif key_code == wx.WXK_HOME:
                self.message_list.SetSelection(0)
            elif key_code == wx.WXK_END:
                self.message_list.SetSelection(len(self.messages) - 1)
            else:
                event.Skip()
        else:
            event.Skip()


# Factory functions for main.py

def show_channel_history(parent, buffer: MessageBuffer,
                        audio: Optional[AudioManager] = None) -> None:
    """Show channel history dialog with multi-channel switcher.

    Shift+F1: All communication channels (BANDO, TELEPATHY, CITIZENSHIP, GROUP)
    """
    dlg = ChannelHistoryDialog(parent, buffer, audio)
    dlg.ShowModal()
    dlg.Destroy()


def show_room_history(parent, buffer: MessageBuffer,
                     audio: Optional[AudioManager] = None) -> None:
    """Show room history dialog (GENERAL channel).

    Shift+F2: Room narration, descriptions, combat text
    """
    dlg = HistoryDialog(parent, "Room History", buffer, ChannelType.GENERAL, audio)
    dlg.ShowModal()
    dlg.Destroy()


def show_telepathy_history(parent, buffer: MessageBuffer,
                          audio: Optional[AudioManager] = None) -> None:
    """Show telepathy history dialog (TELEPATHY channel).

    Shift+F3: Telepathic messages
    """
    dlg = HistoryDialog(parent, "Telepathy History", buffer, ChannelType.TELEPATHY, audio)
    dlg.ShowModal()
    dlg.Destroy()


def show_event_list(parent, buffer: MessageBuffer,
                   audio: Optional[AudioManager] = None) -> None:
    """Show event list dialog (SYSTEM channel).

    Shift+F4: Server messages, system events
    """
    dlg = HistoryDialog(parent, "Event List", buffer, ChannelType.SYSTEM, audio)
    dlg.ShowModal()
    dlg.Destroy()

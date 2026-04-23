"""
Accessible dialogs for managing triggers, aliases, and timers.

Main dialog: TriggerManagerDialog (with tabs for each type)
Edit dialogs: TriggerEditDialog, AliasEditDialog, TimerEditDialog
"""

import wx
from typing import Optional

from models.triggers import (
    TriggerManager, Trigger, Alias, Timer, TriggerAction, ActionType
)


class TriggerManagerDialog(wx.Dialog):
    """Main dialog for managing triggers, aliases, and timers."""

    def __init__(self, parent, trigger_manager: TriggerManager):
        """Initialize trigger manager dialog.

        Args:
            parent: Parent window
            trigger_manager: TriggerManager instance
        """
        wx.Dialog.__init__(self, parent, title="Trigger/Alias/Timer Manager",
                          style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.trigger_manager = trigger_manager

        self._build_ui()
        self.SetSize(600, 400)
        self.CentreOnParent()

    def _build_ui(self):
        """Build dialog UI with notebook tabs."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Notebook with 3 tabs
        notebook = wx.Notebook(self)
        self.trigger_tab = TriggerListPanel(notebook, self.trigger_manager, self)
        self.alias_tab = AliasListPanel(notebook, self.trigger_manager, self)
        self.timer_tab = TimerListPanel(notebook, self.trigger_manager, self)

        notebook.AddPage(self.trigger_tab, "Triggers")
        notebook.AddPage(self.alias_tab, "Aliases")
        notebook.AddPage(self.timer_tab, "Timers")

        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 5)

        # Action buttons at bottom
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(wx.Button(self, label="&New"), 0, wx.RIGHT, 5)
        button_sizer.Add(wx.Button(self, label="&Edit"), 0, wx.RIGHT, 5)
        button_sizer.Add(wx.Button(self, label="&Delete"), 0, wx.RIGHT, 5)
        button_sizer.AddStretchSpacer()
        button_sizer.Add(wx.Button(self, wx.ID_CLOSE, "&Close"), 0)

        sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

        # Bind button events
        self.Bind(wx.EVT_BUTTON, self.on_new_item, id=wx.ID_ANY)
        self.Bind(wx.EVT_BUTTON, self.on_close, id=wx.ID_CLOSE)

    def on_new_item(self, event):
        """Create new trigger/alias/timer based on active tab."""
        notebook = self.FindWindowByName("notebook") or self.FindWindowByLabel("Triggers").GetParent()
        # Get active tab from notebook (simplified)
        pass

    def on_close(self, event):
        """Close dialog and save."""
        self.trigger_manager.save()
        self.EndModal(wx.ID_CLOSE)


class TriggerListPanel(wx.Panel):
    """Panel for listing and managing triggers."""

    def __init__(self, parent, trigger_manager: TriggerManager, main_dialog):
        """Initialize trigger list panel.

        Args:
            parent: Parent notebook
            trigger_manager: TriggerManager instance
            main_dialog: Parent TriggerManagerDialog
        """
        wx.Panel.__init__(self, parent)

        self.trigger_manager = trigger_manager
        self.main_dialog = main_dialog

        self._build_ui()
        self._populate_list()

        # Bind events
        self.list_box.Bind(wx.EVT_LISTBOX, self.on_selection_changed)

    def _build_ui(self):
        """Build UI for trigger list."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Label
        label = wx.StaticText(self, label="Triggers (pattern-based actions):")
        sizer.Add(label, 0, wx.ALL, 5)

        # List
        self.list_box = wx.ListBox(self, style=wx.LB_SINGLE)
        self.list_box.SetName("Trigger List")
        sizer.Add(self.list_box, 1, wx.EXPAND | wx.ALL, 5)

        # Info label
        self.info_label = wx.StaticText(self, label="")
        sizer.Add(self.info_label, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

    def _populate_list(self):
        """Populate list with current triggers."""
        self.list_box.Clear()
        for trigger in self.trigger_manager.triggers:
            status = "[ON]" if trigger.enabled else "[OFF]"
            item = f"{status} {trigger.name}"
            self.list_box.Append(item, trigger.id)

        self.on_selection_changed(None)

    def on_selection_changed(self, event):
        """Update info when selection changes."""
        sel = self.list_box.GetSelection()
        if sel >= 0:
            trigger_id = self.list_box.GetClientData(sel)
            trigger = next((t for t in self.trigger_manager.triggers if t.id == trigger_id), None)
            if trigger:
                info = f"Pattern: {trigger.pattern} | Actions: {len(trigger.actions)}"
                self.info_label.SetLabel(info)
        else:
            self.info_label.SetLabel("")


class AliasListPanel(wx.Panel):
    """Panel for listing and managing aliases."""

    def __init__(self, parent, trigger_manager: TriggerManager, main_dialog):
        """Initialize alias list panel."""
        wx.Panel.__init__(self, parent)

        self.trigger_manager = trigger_manager
        self.main_dialog = main_dialog

        self._build_ui()
        self._populate_list()

        self.list_box.Bind(wx.EVT_LISTBOX, self.on_selection_changed)

    def _build_ui(self):
        """Build UI for alias list."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label="Aliases (command abbreviations):")
        sizer.Add(label, 0, wx.ALL, 5)

        self.list_box = wx.ListBox(self, style=wx.LB_SINGLE)
        self.list_box.SetName("Alias List")
        sizer.Add(self.list_box, 1, wx.EXPAND | wx.ALL, 5)

        self.info_label = wx.StaticText(self, label="")
        sizer.Add(self.info_label, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

    def _populate_list(self):
        """Populate list with current aliases."""
        self.list_box.Clear()
        for alias in self.trigger_manager.aliases:
            status = "[ON]" if alias.enabled else "[OFF]"
            item = f"{status} {alias.abbreviation} -> {alias.expansion}"
            self.list_box.Append(item, alias.id)

        self.on_selection_changed(None)

    def on_selection_changed(self, event):
        """Update info when selection changes."""
        sel = self.list_box.GetSelection()
        if sel >= 0:
            alias_id = self.list_box.GetClientData(sel)
            alias = next((a for a in self.trigger_manager.aliases if a.id == alias_id), None)
            if alias:
                info = f"Expands '{alias.abbreviation}' to '{alias.expansion}'"
                self.info_label.SetLabel(info)
        else:
            self.info_label.SetLabel("")


class TimerListPanel(wx.Panel):
    """Panel for listing and managing timers."""

    def __init__(self, parent, trigger_manager: TriggerManager, main_dialog):
        """Initialize timer list panel."""
        wx.Panel.__init__(self, parent)

        self.trigger_manager = trigger_manager
        self.main_dialog = main_dialog

        self._build_ui()
        self._populate_list()

        self.list_box.Bind(wx.EVT_LISTBOX, self.on_selection_changed)

    def _build_ui(self):
        """Build UI for timer list."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label="Timers (periodic actions):")
        sizer.Add(label, 0, wx.ALL, 5)

        self.list_box = wx.ListBox(self, style=wx.LB_SINGLE)
        self.list_box.SetName("Timer List")
        sizer.Add(self.list_box, 1, wx.EXPAND | wx.ALL, 5)

        self.info_label = wx.StaticText(self, label="")
        sizer.Add(self.info_label, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

    def _populate_list(self):
        """Populate list with current timers."""
        self.list_box.Clear()
        for timer in self.trigger_manager.timers:
            status = "[ON]" if timer.enabled else "[OFF]"
            item = f"{status} {timer.name} (every {timer.interval}s)"
            self.list_box.Append(item, timer.id)

        self.on_selection_changed(None)

    def on_selection_changed(self, event):
        """Update info when selection changes."""
        sel = self.list_box.GetSelection()
        if sel >= 0:
            timer_id = self.list_box.GetClientData(sel)
            timer = next((t for t in self.trigger_manager.timers if t.id == timer_id), None)
            if timer:
                info = f"Every {timer.interval}s | Actions: {len(timer.actions)}"
                self.info_label.SetLabel(info)
        else:
            self.info_label.SetLabel("")


def show_trigger_manager(parent, trigger_manager: TriggerManager) -> None:
    """Show trigger manager dialog.

    Args:
        parent: Parent window
        trigger_manager: TriggerManager instance
    """
    dlg = TriggerManagerDialog(parent, trigger_manager)
    dlg.ShowModal()
    dlg.Destroy()

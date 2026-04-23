"""
Accessible dialogs for managing triggers, aliases, and timers.

Main dialog: TriggerManagerDialog (with tabs for each type)
Edit dialogs: TriggerEditDialog, AliasEditDialog, TimerEditDialog
"""

import wx
from typing import Optional
from uuid import uuid4

from models.triggers import (
    TriggerManager, Trigger, Alias, Timer, TriggerAction, ActionType
)

# Available fields for conditions (from CharacterState)
CONDITION_FIELDS = [
    "hp_pct", "mp_pct", "hp", "maxhp", "mp", "maxmp",
    "nivel", "in_combat", "is_target", "clase", "raza", "name"
]

# Operators for conditions
CONDITION_OPERATORS = ["==", "<", ">", "<=", ">=", "in", "not_in"]

# Storage operations
STORAGE_OPERATIONS = ["add", "remove", "set", "update", "clear"]
STORAGE_FIELDS = ["buffs", "debuffs", "hp_threshold_flags", "last_state", "state_history"]


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
        self.notebook = None
        self.trigger_panel = None
        self.alias_panel = None
        self.timer_panel = None
        self.new_btn = None
        self.edit_btn = None
        self.delete_btn = None

        self._build_ui()
        self.SetSize(600, 400)
        self.CentreOnParent()

    def _build_ui(self):
        """Build dialog UI with notebook tabs."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Notebook with 3 tabs
        self.notebook = wx.Notebook(self)
        self.trigger_panel = TriggerListPanel(self.notebook, self.trigger_manager)
        self.alias_panel = AliasListPanel(self.notebook, self.trigger_manager)
        self.timer_panel = TimerListPanel(self.notebook, self.trigger_manager)

        self.notebook.AddPage(self.trigger_panel, "Triggers")
        self.notebook.AddPage(self.alias_panel, "Aliases")
        self.notebook.AddPage(self.timer_panel, "Timers")

        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        # Action buttons at bottom
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.new_btn = wx.Button(self, label="&Nuevo")
        self.edit_btn = wx.Button(self, label="&Editar")
        self.delete_btn = wx.Button(self, label="&Borrar")
        close_btn = wx.Button(self, wx.ID_CLOSE, "&Cerrar")

        button_sizer.Add(self.new_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(self.edit_btn, 0, wx.RIGHT, 5)
        button_sizer.Add(self.delete_btn, 0, wx.RIGHT, 5)
        button_sizer.AddStretchSpacer()
        button_sizer.Add(close_btn, 0)

        sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

        # Bind button events (explicit bindings, not id=wx.ID_ANY)
        self.Bind(wx.EVT_BUTTON, self.on_new, self.new_btn)
        self.Bind(wx.EVT_BUTTON, self.on_edit, self.edit_btn)
        self.Bind(wx.EVT_BUTTON, self.on_delete, self.delete_btn)
        self.Bind(wx.EVT_BUTTON, self.on_close, id=wx.ID_CLOSE)

    def get_active_panel(self):
        """Get the currently active list panel."""
        idx = self.notebook.GetSelection()
        panels = [self.trigger_panel, self.alias_panel, self.timer_panel]
        return panels[idx] if 0 <= idx < len(panels) else None

    def on_new(self, event):
        """Create new trigger/alias/timer based on active tab."""
        panel = self.get_active_panel()
        if not panel:
            return

        if isinstance(panel, TriggerListPanel):
            dlg = TriggerEditDialog(self, self.trigger_manager)
            if dlg.ShowModal() == wx.ID_OK:
                self.trigger_manager.add_trigger(dlg.get_result())
                panel.refresh()
            dlg.Destroy()
        elif isinstance(panel, AliasListPanel):
            dlg = AliasEditDialog(self, self.trigger_manager)
            if dlg.ShowModal() == wx.ID_OK:
                self.trigger_manager.add_alias(dlg.get_result())
                panel.refresh()
            dlg.Destroy()
        elif isinstance(panel, TimerListPanel):
            dlg = TimerEditDialog(self, self.trigger_manager)
            if dlg.ShowModal() == wx.ID_OK:
                self.trigger_manager.add_timer(dlg.get_result())
                panel.refresh()
            dlg.Destroy()

    def on_edit(self, event):
        """Edit selected trigger/alias/timer."""
        panel = self.get_active_panel()
        if not panel:
            return

        item_id = panel.get_selected_id()
        if not item_id:
            return

        if isinstance(panel, TriggerListPanel):
            trigger = next((t for t in self.trigger_manager.triggers if t.id == item_id), None)
            if trigger:
                dlg = TriggerEditDialog(self, self.trigger_manager, trigger)
                if dlg.ShowModal() == wx.ID_OK:
                    self.trigger_manager.add_trigger(dlg.get_result())
                    panel.refresh()
                dlg.Destroy()
        elif isinstance(panel, AliasListPanel):
            alias = next((a for a in self.trigger_manager.aliases if a.id == item_id), None)
            if alias:
                dlg = AliasEditDialog(self, self.trigger_manager, alias)
                if dlg.ShowModal() == wx.ID_OK:
                    self.trigger_manager.add_alias(dlg.get_result())
                    panel.refresh()
                dlg.Destroy()
        elif isinstance(panel, TimerListPanel):
            timer = next((t for t in self.trigger_manager.timers if t.id == item_id), None)
            if timer:
                dlg = TimerEditDialog(self, self.trigger_manager, timer)
                if dlg.ShowModal() == wx.ID_OK:
                    self.trigger_manager.add_timer(dlg.get_result())
                    panel.refresh()
                dlg.Destroy()

    def on_delete(self, event):
        """Delete selected trigger/alias/timer."""
        panel = self.get_active_panel()
        if not panel:
            return

        item_id = panel.get_selected_id()
        if not item_id:
            return

        if isinstance(panel, TriggerListPanel):
            self.trigger_manager.remove_trigger(item_id)
        elif isinstance(panel, AliasListPanel):
            self.trigger_manager.remove_alias(item_id)
        elif isinstance(panel, TimerListPanel):
            self.trigger_manager.remove_timer(item_id)

        panel.refresh()

    def on_close(self, event):
        """Close dialog and save."""
        self.trigger_manager.save()
        self.EndModal(wx.ID_CLOSE)


class TriggerListPanel(wx.Panel):
    """Panel for listing and managing triggers."""

    def __init__(self, parent, trigger_manager: TriggerManager):
        """Initialize trigger list panel.

        Args:
            parent: Parent notebook
            trigger_manager: TriggerManager instance
        """
        wx.Panel.__init__(self, parent)

        self.trigger_manager = trigger_manager
        self._build_ui()
        self.refresh()
        self.list_box.Bind(wx.EVT_LISTBOX, self.on_selection_changed)

    def _build_ui(self):
        """Build UI for trigger list."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label="Triggers (pattern-based actions):")
        sizer.Add(label, 0, wx.ALL, 5)

        self.list_box = wx.ListBox(self, style=wx.LB_SINGLE)
        self.list_box.SetName("Trigger List")
        sizer.Add(self.list_box, 1, wx.EXPAND | wx.ALL, 5)

        self.info_label = wx.StaticText(self, label="")
        sizer.Add(self.info_label, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

    def refresh(self):
        """Refresh list from TriggerManager."""
        self.list_box.Clear()
        for trigger in self.trigger_manager.triggers:
            status = "[ON]" if trigger.enabled else "[OFF]"
            item = f"{status} {trigger.name}"
            self.list_box.Append(item, trigger.id)
        self.on_selection_changed(None)

    def get_selected_id(self) -> Optional[str]:
        """Get ID of selected trigger, or None."""
        sel = self.list_box.GetSelection()
        if sel == wx.NOT_FOUND:
            return None
        return self.list_box.GetClientData(sel)

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

    def __init__(self, parent, trigger_manager: TriggerManager):
        """Initialize alias list panel."""
        wx.Panel.__init__(self, parent)

        self.trigger_manager = trigger_manager
        self._build_ui()
        self.refresh()
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

    def refresh(self):
        """Refresh list from TriggerManager."""
        self.list_box.Clear()
        for alias in self.trigger_manager.aliases:
            status = "[ON]" if alias.enabled else "[OFF]"
            item = f"{status} {alias.abbreviation} -> {alias.expansion}"
            self.list_box.Append(item, alias.id)
        self.on_selection_changed(None)

    def get_selected_id(self) -> Optional[str]:
        """Get ID of selected alias, or None."""
        sel = self.list_box.GetSelection()
        if sel == wx.NOT_FOUND:
            return None
        return self.list_box.GetClientData(sel)

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

    def __init__(self, parent, trigger_manager: TriggerManager):
        """Initialize timer list panel."""
        wx.Panel.__init__(self, parent)

        self.trigger_manager = trigger_manager
        self._build_ui()
        self.refresh()
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

    def refresh(self):
        """Refresh list from TriggerManager."""
        self.list_box.Clear()
        for timer in self.trigger_manager.timers:
            status = "[ON]" if timer.enabled else "[OFF]"
            item = f"{status} {timer.name} (every {timer.interval}s)"
            self.list_box.Append(item, timer.id)
        self.on_selection_changed(None)

    def get_selected_id(self) -> Optional[str]:
        """Get ID of selected timer, or None."""
        sel = self.list_box.GetSelection()
        if sel == wx.NOT_FOUND:
            return None
        return self.list_box.GetClientData(sel)

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


class TriggerEditDialog(wx.Dialog):
    """Dialog for creating/editing a trigger."""

    def __init__(self, parent, trigger_manager: TriggerManager, trigger: Optional[Trigger] = None):
        """Initialize trigger edit dialog.

        Args:
            parent: Parent window
            trigger_manager: TriggerManager instance (for new_id)
            trigger: Existing trigger to edit, or None for new
        """
        wx.Dialog.__init__(self, parent, title="Edit Trigger",
                          style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.trigger_manager = trigger_manager
        self.editing = trigger is not None
        self._trigger = trigger or Trigger(id=trigger_manager.new_id(), name="", pattern="")
        self._actions = list(self._trigger.actions) if trigger else []
        self._conditions = list(self._trigger.conditions) if trigger else []

        self._build_ui()
        self.SetSize(700, 600)
        self.CentreOnParent()

        if trigger:
            self._populate_from_trigger(trigger)

    def _build_ui(self):
        """Build dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Name
        sizer.Add(wx.StaticText(self, label="Nombre:"), 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)
        self.name_ctrl = wx.TextCtrl(self)
        self.name_ctrl.SetName("Nombre")
        sizer.Add(self.name_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Pattern
        sizer.Add(wx.StaticText(self, label="Patrón:"), 0, wx.LEFT | wx.RIGHT, 5)
        self.pattern_ctrl = wx.TextCtrl(self)
        self.pattern_ctrl.SetName("Patrón")
        sizer.Add(self.pattern_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Regex checkbox
        self.regex_check = wx.CheckBox(self, label="Es expresión regular")
        self.regex_check.SetName("Es expresión regular")
        sizer.Add(self.regex_check, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Conditions group
        cond_box = wx.StaticBox(self, label="Condiciones (AND)")
        cond_sizer = wx.StaticBoxSizer(cond_box, wx.VERTICAL)

        # Add condition panel
        add_cond_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_cond_sizer.Add(wx.StaticText(self, label="Campo:"), 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)

        self.cond_field = wx.Choice(self, choices=CONDITION_FIELDS)
        self.cond_field.SetSelection(0)
        self.cond_field.SetName("Campo de condición")
        add_cond_sizer.Add(self.cond_field, 0, wx.RIGHT, 3)

        add_cond_sizer.Add(wx.StaticText(self, label="Op:"), 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
        self.cond_op = wx.Choice(self, choices=CONDITION_OPERATORS)
        self.cond_op.SetSelection(0)
        self.cond_op.SetName("Operador")
        add_cond_sizer.Add(self.cond_op, 0, wx.RIGHT, 3)

        add_cond_sizer.Add(wx.StaticText(self, label="Valor:"), 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
        self.cond_value = wx.TextCtrl(self, size=(80, -1))
        self.cond_value.SetName("Valor de condición")
        add_cond_sizer.Add(self.cond_value, 0, wx.RIGHT, 3)

        self.add_cond_btn = wx.Button(self, label="&Añadir")
        self.add_cond_btn.Bind(wx.EVT_BUTTON, self.on_add_condition)
        add_cond_sizer.Add(self.add_cond_btn, 0)

        cond_sizer.Add(add_cond_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Conditions list
        self.cond_list = wx.ListBox(self, style=wx.LB_SINGLE, size=(-1, 60))
        self.cond_list.SetName("Lista de condiciones")
        cond_sizer.Add(self.cond_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.remove_cond_btn = wx.Button(self, label="&Quitar condición")
        self.remove_cond_btn.Bind(wx.EVT_BUTTON, self.on_remove_condition)
        cond_sizer.Add(self.remove_cond_btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        sizer.Add(cond_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Actions group
        action_box = wx.StaticBox(self, label="Acciones")
        action_sizer = wx.StaticBoxSizer(action_box, wx.VERTICAL)

        # Action add panel
        add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_sizer.Add(wx.StaticText(self, label="Tipo:"), 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.action_type = wx.Choice(self, choices=["TTS", "SOUND", "GAG", "STORAGE"])
        self.action_type.SetSelection(0)
        self.action_type.SetName("Tipo de acción")
        self.action_type.Bind(wx.EVT_CHOICE, self.on_action_type_changed)
        add_sizer.Add(self.action_type, 0, wx.RIGHT, 5)

        add_sizer.Add(wx.StaticText(self, label="Valor:"), 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.action_value = wx.TextCtrl(self)
        self.action_value.SetName("Valor de acción")
        add_sizer.Add(self.action_value, 1, wx.EXPAND | wx.RIGHT, 5)

        # Storage operation selector (shown only for STORAGE actions)
        add_sizer.Add(wx.StaticText(self, label="Op:"), 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.storage_op = wx.Choice(self, choices=STORAGE_OPERATIONS)
        self.storage_op.SetSelection(0)
        self.storage_op.SetName("Operación de storage")
        self.storage_op.Hide()
        add_sizer.Add(self.storage_op, 0, wx.RIGHT, 5)

        self.add_action_btn = wx.Button(self, label="&Añadir")
        self.add_action_btn.Bind(wx.EVT_BUTTON, self.on_add_action)
        add_sizer.Add(self.add_action_btn, 0)

        action_sizer.Add(add_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Actions list
        self.action_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.action_list.SetName("Lista de acciones")
        action_sizer.Add(self.action_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.remove_action_btn = wx.Button(self, label="&Quitar acción")
        self.remove_action_btn.Bind(wx.EVT_BUTTON, self.on_remove_action)
        action_sizer.Add(self.remove_action_btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        sizer.Add(action_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # Enabled checkbox
        self.enabled_check = wx.CheckBox(self, label="Habilitado")
        self.enabled_check.SetValue(True)
        self.enabled_check.SetName("Habilitado")
        sizer.Add(self.enabled_check, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(wx.Button(self, wx.ID_OK, "&Aceptar"), 0, wx.RIGHT, 5)
        btn_sizer.Add(wx.Button(self, wx.ID_CANCEL, "Cancelar"), 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

    def on_action_type_changed(self, event):
        """Enable/disable action_value based on type."""
        action_type = self.action_type.GetStringSelection()
        is_gag = action_type == "GAG"
        is_storage = action_type == "STORAGE"

        self.action_value.Enable(not is_gag and not is_storage)
        if hasattr(self, 'storage_op'):
            if is_storage:
                self.storage_op.Show()
            else:
                self.storage_op.Hide()
            self.Layout()

    def on_add_action(self, event):
        """Add action to list."""
        action_type_str = self.action_type.GetStringSelection()

        # Map string to ActionType
        action_type_map = {
            "TTS": ActionType.TTS,
            "SOUND": ActionType.SOUND,
            "GAG": ActionType.GAG,
            "STORAGE": ActionType.STORAGE
        }
        action_type = action_type_map.get(action_type_str, ActionType.TTS)

        # Get value (TTS, SOUND, STORAGE)
        value = self.action_value.GetValue() if action_type_str != "GAG" else ""

        # For STORAGE, get operation
        operation = self.storage_op.GetStringSelection() if action_type_str == "STORAGE" else ""

        action = TriggerAction(
            action_type=action_type,
            value=value,
            operation=operation,
            data=""
        )
        self._actions.append(action)

        self._refresh_action_list()
        self.action_value.SetValue("")

    def on_remove_action(self, event):
        """Remove selected action from list."""
        sel = self.action_list.GetSelection()
        if sel >= 0:
            del self._actions[sel]
            self._refresh_action_list()

    def on_add_condition(self, event):
        """Add condition to list."""
        field = self.cond_field.GetStringSelection()
        operator = self.cond_op.GetStringSelection()
        value = self.cond_value.GetValue()

        if not field or not operator or not value:
            return

        # Parse value based on operator/field
        try:
            if operator in ["<", ">", "<=", ">="] or field.endswith("_pct"):
                # Numeric comparison
                value = int(value)
            elif operator in ["in", "not_in"]:
                # List of values (comma-separated)
                value = [v.strip() for v in value.split(",")]
        except ValueError:
            pass

        condition = {
            "field": field,
            "operator": operator,
            "value": value
        }
        self._conditions.append(condition)
        self._refresh_condition_list()
        self.cond_value.SetValue("")

    def on_remove_condition(self, event):
        """Remove selected condition from list."""
        sel = self.cond_list.GetSelection()
        if sel >= 0:
            del self._conditions[sel]
            self._refresh_condition_list()

    def _refresh_action_list(self):
        """Refresh displayed action list."""
        self.action_list.Clear()
        for action in self._actions:
            if action.action_type == ActionType.TTS:
                text = f"TTS: {action.value}"
            elif action.action_type == ActionType.SOUND:
                text = f"SOUND: {action.value}"
            elif action.action_type == ActionType.STORAGE:
                text = f"STORAGE: {action.operation} {action.value}"
            else:
                text = "GAG"
            self.action_list.Append(text)

    def _refresh_condition_list(self):
        """Refresh displayed condition list."""
        self.cond_list.Clear()
        for cond in self._conditions:
            text = f"{cond['field']} {cond['operator']} {cond['value']}"
            self.cond_list.Append(text)

    def _populate_from_trigger(self, trigger: Trigger):
        """Populate dialog from existing trigger."""
        self.name_ctrl.SetValue(trigger.name)
        self.pattern_ctrl.SetValue(trigger.pattern)
        self.regex_check.SetValue(trigger.is_regex)
        self.enabled_check.SetValue(trigger.enabled)
        self._refresh_action_list()
        self._refresh_condition_list()

    def get_result(self) -> Trigger:
        """Build and return Trigger from dialog values."""
        return Trigger(
            id=self._trigger.id,
            name=self.name_ctrl.GetValue(),
            pattern=self.pattern_ctrl.GetValue(),
            is_regex=self.regex_check.GetValue(),
            actions=self._actions,
            enabled=self.enabled_check.GetValue(),
            conditions=self._conditions
        )


class AliasEditDialog(wx.Dialog):
    """Dialog for creating/editing an alias."""

    def __init__(self, parent, trigger_manager: TriggerManager, alias: Optional[Alias] = None):
        """Initialize alias edit dialog.

        Args:
            parent: Parent window
            trigger_manager: TriggerManager instance (for new_id)
            alias: Existing alias to edit, or None for new
        """
        wx.Dialog.__init__(self, parent, title="Edit Alias",
                          style=wx.DEFAULT_DIALOG_STYLE)

        self.trigger_manager = trigger_manager
        self.editing = alias is not None
        self._alias = alias or Alias(id=trigger_manager.new_id(), abbreviation="", expansion="")

        self._build_ui()
        self.SetSize(400, 200)
        self.CentreOnParent()

        if alias:
            self._populate_from_alias(alias)

    def _build_ui(self):
        """Build dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Abbreviation
        sizer.Add(wx.StaticText(self, label="Abreviatura:"), 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)
        self.abbr_ctrl = wx.TextCtrl(self)
        self.abbr_ctrl.SetName("Abreviatura")
        sizer.Add(self.abbr_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Expansion
        sizer.Add(wx.StaticText(self, label="Expansión:"), 0, wx.LEFT | wx.RIGHT, 5)
        self.exp_ctrl = wx.TextCtrl(self)
        self.exp_ctrl.SetName("Expansión")
        sizer.Add(self.exp_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Enabled checkbox
        self.enabled_check = wx.CheckBox(self, label="Habilitado")
        self.enabled_check.SetValue(True)
        self.enabled_check.SetName("Habilitado")
        sizer.Add(self.enabled_check, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(wx.Button(self, wx.ID_OK, "&Aceptar"), 0, wx.RIGHT, 5)
        btn_sizer.Add(wx.Button(self, wx.ID_CANCEL, "Cancelar"), 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

    def _populate_from_alias(self, alias: Alias):
        """Populate dialog from existing alias."""
        self.abbr_ctrl.SetValue(alias.abbreviation)
        self.exp_ctrl.SetValue(alias.expansion)
        self.enabled_check.SetValue(alias.enabled)

    def get_result(self) -> Alias:
        """Build and return Alias from dialog values."""
        return Alias(
            id=self._alias.id,
            abbreviation=self.abbr_ctrl.GetValue(),
            expansion=self.exp_ctrl.GetValue(),
            enabled=self.enabled_check.GetValue()
        )


class TimerEditDialog(wx.Dialog):
    """Dialog for creating/editing a timer."""

    def __init__(self, parent, trigger_manager: TriggerManager, timer: Optional[Timer] = None):
        """Initialize timer edit dialog.

        Args:
            parent: Parent window
            trigger_manager: TriggerManager instance (for new_id)
            timer: Existing timer to edit, or None for new
        """
        wx.Dialog.__init__(self, parent, title="Edit Timer",
                          style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.trigger_manager = trigger_manager
        self.editing = timer is not None
        self._timer = timer or Timer(id=trigger_manager.new_id(), name="", interval=30)
        self._actions = list(self._timer.actions) if timer else []

        self._build_ui()
        self.SetSize(500, 400)
        self.CentreOnParent()

        if timer:
            self._populate_from_timer(timer)

    def _build_ui(self):
        """Build dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Name
        sizer.Add(wx.StaticText(self, label="Nombre:"), 0, wx.TOP | wx.LEFT | wx.RIGHT, 5)
        self.name_ctrl = wx.TextCtrl(self)
        self.name_ctrl.SetName("Nombre")
        sizer.Add(self.name_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Interval
        sizer.Add(wx.StaticText(self, label="Intervalo (segundos):"), 0, wx.LEFT | wx.RIGHT, 5)
        self.interval_ctrl = wx.TextCtrl(self)
        self.interval_ctrl.SetName("Intervalo")
        sizer.Add(self.interval_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Actions group
        action_box = wx.StaticBox(self, label="Acciones")
        action_sizer = wx.StaticBoxSizer(action_box, wx.VERTICAL)

        # Action add panel
        add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_sizer.Add(wx.StaticText(self, label="Tipo:"), 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.action_type = wx.Choice(self, choices=["TTS", "GAG"])
        self.action_type.SetSelection(0)
        self.action_type.SetName("Tipo de acción")
        self.action_type.Bind(wx.EVT_CHOICE, self.on_action_type_changed)
        add_sizer.Add(self.action_type, 0, wx.RIGHT, 5)

        add_sizer.Add(wx.StaticText(self, label="Valor:"), 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.action_value = wx.TextCtrl(self)
        self.action_value.SetName("Valor de acción")
        add_sizer.Add(self.action_value, 1, wx.EXPAND | wx.RIGHT, 5)

        self.add_action_btn = wx.Button(self, label="&Añadir")
        self.add_action_btn.Bind(wx.EVT_BUTTON, self.on_add_action)
        add_sizer.Add(self.add_action_btn, 0)

        action_sizer.Add(add_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Actions list
        self.action_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.action_list.SetName("Lista de acciones")
        action_sizer.Add(self.action_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.remove_action_btn = wx.Button(self, label="&Quitar acción")
        self.remove_action_btn.Bind(wx.EVT_BUTTON, self.on_remove_action)
        action_sizer.Add(self.remove_action_btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        sizer.Add(action_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # Enabled checkbox
        self.enabled_check = wx.CheckBox(self, label="Habilitado")
        self.enabled_check.SetValue(True)
        self.enabled_check.SetName("Habilitado")
        sizer.Add(self.enabled_check, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(wx.Button(self, wx.ID_OK, "&Aceptar"), 0, wx.RIGHT, 5)
        btn_sizer.Add(wx.Button(self, wx.ID_CANCEL, "Cancelar"), 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)

    def on_action_type_changed(self, event):
        """Enable/disable action_value based on type."""
        action_type = self.action_type.GetStringSelection()
        is_gag = action_type == "GAG"
        is_storage = action_type == "STORAGE"

        self.action_value.Enable(not is_gag and not is_storage)
        if hasattr(self, 'storage_op'):
            if is_storage:
                self.storage_op.Show()
            else:
                self.storage_op.Hide()
            self.Layout()

    def on_add_action(self, event):
        """Add action to list."""
        action_type_str = self.action_type.GetStringSelection()
        value = self.action_value.GetValue() if action_type_str == "TTS" else ""

        action_type = ActionType.TTS if action_type_str == "TTS" else ActionType.GAG
        action = TriggerAction(action_type=action_type, value=value)
        self._actions.append(action)

        self._refresh_action_list()
        self.action_value.SetValue("")

    def on_remove_action(self, event):
        """Remove selected action from list."""
        sel = self.action_list.GetSelection()
        if sel >= 0:
            del self._actions[sel]
            self._refresh_action_list()

    def _refresh_action_list(self):
        """Refresh displayed action list."""
        self.action_list.Clear()
        for action in self._actions:
            if action.action_type == ActionType.TTS:
                text = f"TTS: {action.value}"
            else:
                text = "GAG"
            self.action_list.Append(text)

    def _populate_from_timer(self, timer: Timer):
        """Populate dialog from existing timer."""
        self.name_ctrl.SetValue(timer.name)
        self.interval_ctrl.SetValue(str(timer.interval))
        self.enabled_check.SetValue(timer.enabled)
        self._refresh_action_list()

    def get_result(self) -> Timer:
        """Build and return Timer from dialog values."""
        try:
            interval = float(self.interval_ctrl.GetValue())
        except ValueError:
            interval = 30

        return Timer(
            id=self._timer.id,
            name=self.name_ctrl.GetValue(),
            interval=interval,
            actions=self._actions,
            enabled=self.enabled_check.GetValue()
        )


def show_trigger_manager(parent, trigger_manager: TriggerManager) -> None:
    """Show trigger manager dialog.

    Args:
        parent: Parent window
        trigger_manager: TriggerManager instance
    """
    dlg = TriggerManagerDialog(parent, trigger_manager)
    dlg.ShowModal()
    dlg.Destroy()

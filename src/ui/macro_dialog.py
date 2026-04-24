"""
Macro Dialog - UI for managing and editing macros.
"""

import wx
import uuid
from models.macro_executor import MacroManager, MacroDefinition, MacroStep


class MacroManagerDialog(wx.Dialog):
    """Dialog for managing macros (list, create, edit, delete)."""

    def __init__(self, parent, macro_manager: MacroManager):
        """Initialize macro manager dialog.

        Args:
            parent: Parent window
            macro_manager: MacroManager instance
        """
        super().__init__(parent, title="Gestionar Macros", size=(600, 450))
        self.macro_manager = macro_manager
        self.Centre()

        self._build_ui()
        self._load_macros()

    def _build_ui(self) -> None:
        """Build dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(self, label="Macros disponibles:")
        title_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.LEFT | wx.TOP, 15)

        # Macro list
        self.macro_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.macro_list.SetName("Lista de macros")
        self.macro_list.Bind(wx.EVT_LISTBOX, self._on_macro_selected)
        sizer.Add(self.macro_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 15)

        # Info label
        self.info_label = wx.StaticText(self, label="Selecciona una macro para más detalles")
        info_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        self.info_label.SetFont(info_font)
        sizer.Add(self.info_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 15)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        new_btn = wx.Button(self, label="&Nuevo")
        new_btn.SetName("Create New Macro")
        new_btn.Bind(wx.EVT_BUTTON, self._on_new)

        edit_btn = wx.Button(self, label="&Editar")
        edit_btn.SetName("Edit Selected Macro")
        edit_btn.Bind(wx.EVT_BUTTON, self._on_edit)

        delete_btn = wx.Button(self, label="&Borrar")
        delete_btn.SetName("Delete Selected Macro")
        delete_btn.Bind(wx.EVT_BUTTON, self._on_delete)

        execute_btn = wx.Button(self, label="&Ejecutar ahora")
        execute_btn.SetName("Execute Macro Now")
        execute_btn.Bind(wx.EVT_BUTTON, self._on_execute)

        btn_sizer.Add(new_btn, 0, wx.RIGHT, 5)
        btn_sizer.Add(edit_btn, 0, wx.RIGHT, 5)
        btn_sizer.Add(delete_btn, 0, wx.RIGHT, 5)
        btn_sizer.Add(execute_btn, 0)
        btn_sizer.AddStretchSpacer()

        close_btn = wx.Button(self, wx.ID_CLOSE, "&Cerrar")
        close_btn.SetName("Close Macro Manager")
        close_btn.Bind(wx.EVT_BUTTON, self._on_close)
        btn_sizer.Add(close_btn, 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        self.SetSizer(sizer)

    def _load_macros(self) -> None:
        """Load macros into list."""
        self.macro_list.Clear()
        for macro in self.macro_manager.macros:
            status = "ON" if macro.enabled else "OFF"
            hotkey_str = macro.hotkey if macro.hotkey else "-"
            label = f"[{status}] {hotkey_str:4} | {macro.name}"
            self.macro_list.Append(label, macro.id)

    def _on_macro_selected(self, event) -> None:
        """Handle macro selection."""
        sel = self.macro_list.GetSelection()
        if sel == wx.NOT_FOUND:
            return

        macro_id = self.macro_list.GetClientData(sel)
        macro = next((m for m in self.macro_manager.macros if m.id == macro_id), None)

        if macro:
            info = f"{macro.name} | {len(macro.steps)} pasos"
            if macro.description:
                info += f" | {macro.description}"
            self.info_label.SetLabel(info)

    def _on_new(self, event) -> None:
        """Create new macro."""
        macro = MacroDefinition(id=str(uuid.uuid4()), name="Nuevo macro")
        dlg = MacroEditDialog(self, macro)
        if dlg.ShowModal() == wx.ID_OK:
            result = dlg.get_result()
            self.macro_manager.add_macro(result)
            self._load_macros()
        dlg.Destroy()

    def _on_edit(self, event) -> None:
        """Edit selected macro."""
        sel = self.macro_list.GetSelection()
        if sel == wx.NOT_FOUND:
            return

        macro_id = self.macro_list.GetClientData(sel)
        macro = next((m for m in self.macro_manager.macros if m.id == macro_id), None)

        if macro:
            dlg = MacroEditDialog(self, macro)
            if dlg.ShowModal() == wx.ID_OK:
                result = dlg.get_result()
                self.macro_manager.add_macro(result)
                self._load_macros()
            dlg.Destroy()

    def _on_delete(self, event) -> None:
        """Delete selected macro."""
        sel = self.macro_list.GetSelection()
        if sel == wx.NOT_FOUND:
            return

        macro_id = self.macro_list.GetClientData(sel)
        macro = next((m for m in self.macro_manager.macros if m.id == macro_id), None)

        if macro:
            dlg = wx.MessageDialog(
                self,
                f"Borrar macro '{macro.name}'?",
                "Confirmar borrado",
                wx.YES_NO | wx.ICON_WARNING
            )
            if dlg.ShowModal() == wx.ID_YES:
                self.macro_manager.remove_macro(macro_id)
                self._load_macros()
            dlg.Destroy()

    def _on_execute(self, event) -> None:
        """Execute selected macro immediately."""
        sel = self.macro_list.GetSelection()
        if sel == wx.NOT_FOUND:
            return

        macro_id = self.macro_list.GetClientData(sel)
        macro = next((m for m in self.macro_manager.macros if m.id == macro_id), None)

        if macro:
            self.macro_manager.execute(macro)

    def _on_close(self, event) -> None:
        """Close dialog."""
        self.EndModal(wx.ID_CLOSE)


class MacroEditDialog(wx.Dialog):
    """Dialog for editing a macro definition."""

    def __init__(self, parent, macro: MacroDefinition):
        """Initialize macro edit dialog.

        Args:
            parent: Parent window
            macro: MacroDefinition to edit (None for new)
        """
        super().__init__(parent, title="Editar Macro", size=(650, 550))
        self.macro = macro
        self.current_steps = list(macro.steps)
        self.Centre()

        self._build_ui()
        self._load_data()

    def _build_ui(self) -> None:
        """Build dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Nombre
        name_label = wx.StaticText(self, label="Nombre:")
        sizer.Add(name_label, 0, wx.LEFT | wx.TOP, 15)

        self.name_ctrl = wx.TextCtrl(self, value=self.macro.name)
        self.name_ctrl.SetName("Nombre de macro")
        sizer.Add(self.name_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)

        # Hotkey
        hotkey_label = wx.StaticText(self, label="Hotkey:")
        sizer.Add(hotkey_label, 0, wx.LEFT | wx.TOP, 15)

        self.hotkey_choice = wx.Choice(self, choices=["Sin hotkey", "F12", "F13", "F14", "F15"])
        self.hotkey_choice.SetName("Hotkey")
        if self.macro.hotkey in ["F12", "F13", "F14", "F15"]:
            self.hotkey_choice.SetStringSelection(self.macro.hotkey)
        else:
            self.hotkey_choice.SetSelection(0)
        sizer.Add(self.hotkey_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)

        # Descripción
        desc_label = wx.StaticText(self, label="Descripción:")
        sizer.Add(desc_label, 0, wx.LEFT | wx.TOP, 15)

        self.desc_ctrl = wx.TextCtrl(self, value=self.macro.description)
        self.desc_ctrl.SetName("Descripción de macro")
        sizer.Add(self.desc_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)

        # Steps section
        steps_box = wx.StaticBox(self, label="Pasos de la macro")
        steps_sizer = wx.StaticBoxSizer(steps_box, wx.VERTICAL)

        # Action type
        type_label = wx.StaticText(self, label="Tipo:")
        self.type_choice = wx.Choice(self, choices=["Enviar comando", "Anunciar TTS", "Reproducir sonido"])
        self.type_choice.SetSelection(0)
        self.type_choice.SetName("Tipo de acción")

        type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        type_sizer.Add(type_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        type_sizer.Add(self.type_choice, 1)
        steps_sizer.Add(type_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)

        # Action value
        value_label = wx.StaticText(self, label="Valor:")
        self.value_ctrl = wx.TextCtrl(self)
        self.value_ctrl.SetName("Valor de acción")

        value_sizer = wx.BoxSizer(wx.HORIZONTAL)
        value_sizer.Add(value_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        value_sizer.Add(self.value_ctrl, 1)
        steps_sizer.Add(value_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)

        # Delay
        delay_label = wx.StaticText(self, label="Pausa antes (ms):")
        self.delay_spin = wx.SpinCtrl(self, value=500, min=0, max=30000)
        self.delay_spin.SetName("Pausa en milisegundos")

        delay_sizer = wx.BoxSizer(wx.HORIZONTAL)
        delay_sizer.Add(delay_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        delay_sizer.Add(self.delay_spin, 0)
        steps_sizer.Add(delay_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)

        # Add button
        add_btn = wx.Button(self, label="&Añadir paso")
        add_btn.SetName("Add Step to Macro")
        add_btn.Bind(wx.EVT_BUTTON, self._on_add_step)
        steps_sizer.Add(add_btn, 0)

        # Steps list
        self.steps_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.steps_list.SetName("Lista de pasos")
        steps_sizer.Add(self.steps_list, 1, wx.EXPAND | wx.TOP, 10)

        # Remove button
        remove_btn = wx.Button(self, label="&Quitar paso")
        remove_btn.SetName("Remove Step from Macro")
        remove_btn.Bind(wx.EVT_BUTTON, self._on_remove_step)
        steps_sizer.Add(remove_btn, 0, wx.TOP, 5)

        sizer.Add(steps_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 15)

        # Enabled checkbox
        self.enabled_check = wx.CheckBox(self, label="Habilitado")
        self.enabled_check.SetName("Habilitado")
        self.enabled_check.SetValue(True)
        sizer.Add(self.enabled_check, 0, wx.LEFT | wx.TOP, 15)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self, wx.ID_OK, "&Aceptar")
        cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancelar")
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(ok_btn, 0, wx.RIGHT, 5)
        btn_sizer.Add(cancel_btn, 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)

        self.SetSizer(sizer)

    def _load_data(self) -> None:
        """Load macro data into controls."""
        self.enabled_check.SetValue(self.macro.enabled)
        self._refresh_steps()

    def _refresh_steps(self) -> None:
        """Refresh steps list display."""
        self.steps_list.Clear()
        for step in self.current_steps:
            action_str = {
                "send": "Enviar",
                "tts": "TTS",
                "sound": "Sonido"
            }.get(step.action_type, step.action_type)

            label = f"{step.delay_before_ms}ms | {action_str}: {step.value[:30]}"
            if len(step.value) > 30:
                label += "..."
            self.steps_list.Append(label)

    def _on_add_step(self, event) -> None:
        """Add new step."""
        action_types = {0: "send", 1: "tts", 2: "sound"}
        action_type = action_types[self.type_choice.GetSelection()]
        value = self.value_ctrl.GetValue().strip()
        delay = self.delay_spin.GetValue()

        if not value:
            return

        step = MacroStep(
            action_type=action_type,
            value=value,
            delay_before_ms=delay
        )
        self.current_steps.append(step)
        self._refresh_steps()

        # Clear inputs
        self.value_ctrl.SetValue("")
        self.delay_spin.SetValue(500)

    def _on_remove_step(self, event) -> None:
        """Remove selected step."""
        sel = self.steps_list.GetSelection()
        if sel != wx.NOT_FOUND:
            del self.current_steps[sel]
            self._refresh_steps()

    def get_result(self) -> MacroDefinition:
        """Get edited macro definition.

        Returns:
            MacroDefinition with updated values
        """
        hotkey = self.hotkey_choice.GetStringSelection()
        if hotkey == "Sin hotkey":
            hotkey = ""

        return MacroDefinition(
            id=self.macro.id,
            name=self.name_ctrl.GetValue().strip(),
            hotkey=hotkey,
            steps=self.current_steps,
            enabled=self.enabled_check.GetValue(),
            description=self.desc_ctrl.GetValue().strip()
        )


def show_macro_manager(parent, macro_manager: MacroManager) -> None:
    """Show macro manager dialog (modal).

    Args:
        parent: Parent window
        macro_manager: MacroManager instance
    """
    dlg = MacroManagerDialog(parent, macro_manager)
    dlg.ShowModal()
    dlg.Destroy()

"""
Interactive prompt dialogs for character setup and game configuration.
wxPython dialogs for class selection, game modes, and preferences.

Phase 6E: UI dialogs for initial character setup and settings.
"""

import wx
from typing import Optional, List, Dict, Any


class ClassSelectionDialog(wx.Dialog):
    """Dialog for selecting character class."""

    def __init__(self, parent=None):
        super().__init__(
            parent,
            title="Selecciona tu Clase",
            size=(400, 500),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        self.selected_class = None
        self._build_ui()
        self.Center()

    def _build_ui(self):
        """Build the dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Message
        msg = wx.StaticText(self, label="Clases Disponibles:")
        sizer.Add(msg, 0, wx.ALL | wx.EXPAND, 10)

        # Class list
        classes = [
            "Soldado", "Mago", "Clérigo", "Druida", "Bardo",
            "Asesino", "Ranger", "Monje", "Nigromante", "Templario",
            "Hechicero", "Brujo", "Alquimista", "Cazador de Dragones",
            "Ermitaño", "Trovador", "Corsario", "Espadachín",
            "Caballero Oscuro", "Paladín", "Khazad"
        ]

        self.class_list = wx.ListBox(self, choices=classes)
        self.class_list.SetSelection(0)
        sizer.Add(self.class_list, 1, wx.ALL | wx.EXPAND, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self, wx.ID_OK, "&Aceptar")
        cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancelar")
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self.on_ok, ok_btn)

    def on_ok(self, event):
        """Handle OK button."""
        sel = self.class_list.GetSelection()
        if sel != wx.NOT_FOUND:
            self.selected_class = self.class_list.GetString(sel)
        self.EndModal(wx.ID_OK)

    def get_selection(self) -> Optional[str]:
        """Get selected class."""
        return self.selected_class


class GameModeDialog(wx.Dialog):
    """Dialog for selecting game mode (Combat/XP/Idle)."""

    def __init__(self, parent=None):
        super().__init__(
            parent,
            title="Modo de Combate",
            size=(400, 300),
            style=wx.DEFAULT_DIALOG_STYLE
        )

        self.selected_mode = None
        self._build_ui()
        self.Center()

    def _build_ui(self):
        """Build the dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Message
        msg = wx.StaticText(self, label="Selecciona el modo de combate:")
        sizer.Add(msg, 0, wx.ALL | wx.EXPAND, 10)

        # Mode selection
        self.mode_choice = wx.Choice(
            self,
            choices=[
                "Combate (Combate activo)",
                "XP (Ganar experiencia)",
                "Idle (Ocio)"
            ]
        )
        self.mode_choice.SetSelection(0)
        self.mode_choice.SetName("Connection Mode Selection")
        sizer.Add(self.mode_choice, 0, wx.ALL | wx.EXPAND, 10)

        # Description
        desc = wx.StaticText(
            self,
            label="Combate: Enfocado en batalla\n"
                  "XP: Enfocado en ganar experiencia\n"
                  "Idle: Modo pasivo"
        )
        sizer.Add(desc, 1, wx.ALL | wx.EXPAND, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self, wx.ID_OK, "&Aceptar")
        cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancelar")
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self.on_ok, ok_btn)

    def on_ok(self, event):
        """Handle OK button."""
        self.selected_mode = self.mode_choice.GetSelection() + 1
        self.EndModal(wx.ID_OK)

    def get_selection(self) -> Optional[int]:
        """Get selected mode (1=Combat, 2=XP, 3=Idle)."""
        return self.selected_mode


class TravelSpeedDialog(wx.Dialog):
    """Dialog for selecting travel speed mode."""

    def __init__(self, parent=None):
        super().__init__(
            parent,
            title="Velocidad de Viaje",
            size=(400, 300),
            style=wx.DEFAULT_DIALOG_STYLE
        )

        self.selected_speed = None
        self._build_ui()
        self.Center()

    def _build_ui(self):
        """Build the dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Message
        msg = wx.StaticText(self, label="Selecciona la velocidad de viaje:")
        sizer.Add(msg, 0, wx.ALL | wx.EXPAND, 10)

        # Speed selection
        self.speed_choice = wx.Choice(
            self,
            choices=[
                "Normal (Velocidad normal)",
                "Turbo (1.5x velocidad)",
                "Ultra (2x velocidad)"
            ]
        )
        self.speed_choice.SetSelection(0)
        self.speed_choice.SetName("Connection Speed Selection")
        sizer.Add(self.speed_choice, 0, wx.ALL | wx.EXPAND, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self, wx.ID_OK, "&Aceptar")
        cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancelar")
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self.on_ok, ok_btn)

    def on_ok(self, event):
        """Handle OK button."""
        self.selected_speed = self.speed_choice.GetSelection()
        self.EndModal(wx.ID_OK)

    def get_selection(self) -> Optional[int]:
        """Get selected speed (0=Normal, 1=Turbo, 2=Ultra)."""
        return self.selected_speed


class YesNoDialog(wx.Dialog):
    """Generic yes/no confirmation dialog."""

    def __init__(self, parent=None, title="Confirmación", message="¿Continuar?"):
        super().__init__(
            parent,
            title=title,
            size=(350, 200),
            style=wx.DEFAULT_DIALOG_STYLE
        )

        self.result = None
        self.message = message
        self._build_ui()
        self.Center()

    def _build_ui(self):
        """Build the dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Message
        msg = wx.StaticText(self, label=self.message)
        sizer.Add(msg, 1, wx.ALL | wx.EXPAND, 20)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        yes_btn = wx.Button(self, wx.ID_YES, "&Sí")
        no_btn = wx.Button(self, wx.ID_NO, "&No")
        btn_sizer.Add(yes_btn, 0, wx.ALL, 5)
        btn_sizer.Add(no_btn, 0, wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self.on_yes, yes_btn)
        self.Bind(wx.EVT_BUTTON, self.on_no, no_btn)

    def on_yes(self, event):
        """Handle Yes button."""
        self.result = 1
        self.EndModal(wx.ID_YES)

    def on_no(self, event):
        """Handle No button."""
        self.result = 0
        self.EndModal(wx.ID_NO)

    def get_result(self) -> Optional[int]:
        """Get result (1=Yes, 0=No)."""
        return self.result


class ListSelectionDialog(wx.Dialog):
    """Generic list selection dialog."""

    def __init__(
        self,
        parent=None,
        title="Selecciona",
        message="Elige una opción:",
        items: List[str] = None,
        ok_label="&Aceptar",
        cancel_label="Cancelar"
    ):
        super().__init__(
            parent,
            title=title,
            size=(400, 400),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        self.items = items or []
        self.message = message
        self.ok_label = ok_label
        self.cancel_label = cancel_label
        self.selected_item = None
        self._build_ui()
        self.Center()

    def _build_ui(self):
        """Build the dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Message
        msg = wx.StaticText(self, label=self.message)
        sizer.Add(msg, 0, wx.ALL | wx.EXPAND, 10)

        # List
        self.list_box = wx.ListBox(self, choices=self.items)
        if self.items:
            self.list_box.SetSelection(0)
        sizer.Add(self.list_box, 1, wx.ALL | wx.EXPAND, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self, wx.ID_OK, self.ok_label)
        cancel_btn = wx.Button(self, wx.ID_CANCEL, self.cancel_label)
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self.on_ok, ok_btn)

    def on_ok(self, event):
        """Handle OK button."""
        sel = self.list_box.GetSelection()
        if sel != wx.NOT_FOUND:
            self.selected_item = self.list_box.GetString(sel)
        self.EndModal(wx.ID_OK)

    def get_selection(self) -> Optional[str]:
        """Get selected item."""
        return self.selected_item


class PromptDialogManager:
    """Manager for all prompt dialogs."""

    @staticmethod
    def show_class_selection(parent=None) -> Optional[str]:
        """Show class selection dialog."""
        dlg = ClassSelectionDialog(parent)
        dlg.ShowModal()
        result = dlg.get_selection()
        dlg.Destroy()
        return result

    @staticmethod
    def show_game_mode(parent=None) -> Optional[int]:
        """Show game mode dialog."""
        dlg = GameModeDialog(parent)
        dlg.ShowModal()
        result = dlg.get_selection()
        dlg.Destroy()
        return result

    @staticmethod
    def show_travel_speed(parent=None) -> Optional[int]:
        """Show travel speed dialog."""
        dlg = TravelSpeedDialog(parent)
        dlg.ShowModal()
        result = dlg.get_selection()
        dlg.Destroy()
        return result

    @staticmethod
    def show_yes_no(parent=None, title="Confirmación", message="¿Continuar?") -> Optional[int]:
        """Show yes/no dialog."""
        dlg = YesNoDialog(parent, title, message)
        dlg.ShowModal()
        result = dlg.get_result()
        dlg.Destroy()
        return result

    @staticmethod
    def show_list(
        parent=None,
        title="Selecciona",
        message="Elige una opción:",
        items: List[str] = None,
        ok_label="&Aceptar",
        cancel_label="Cancelar"
    ) -> Optional[str]:
        """Show list selection dialog."""
        dlg = ListSelectionDialog(parent, title, message, items, ok_label, cancel_label)
        dlg.ShowModal()
        result = dlg.get_selection()
        dlg.Destroy()
        return result

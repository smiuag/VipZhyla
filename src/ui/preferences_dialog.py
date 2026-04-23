"""
Preferences Dialog - User configurable settings for VipZhyla
"""

import wx
import json
from pathlib import Path


class PreferencesDialog(wx.Dialog):
    """Dialog for user preferences (encoding, audio, etc.)."""

    def __init__(self, parent, current_encoding="UTF-8"):
        """Initialize preferences dialog.

        Args:
            parent: Parent window
            current_encoding: Current character encoding (default: UTF-8)
        """
        super().__init__(parent, title="Preferencias", size=(500, 350))
        self.current_encoding = current_encoding
        self.config_path = Path("src/config/mud_config.json")

        self._build_ui()
        self._load_config()
        self.Centre()

    def _build_ui(self):
        """Build preferences dialog UI."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.SetMinSize((500, 450))

        # Fonts
        header_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        label_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        # === Encoding Section ===
        encoding_box = wx.StaticBox(self, label="Codificación de Caracteres")
        encoding_box_sizer = wx.StaticBoxSizer(encoding_box, wx.VERTICAL)

        encoding_label = wx.StaticText(self, label="Charset:")
        encoding_label.SetFont(label_font)
        encoding_box_sizer.Add(encoding_label, 0, wx.LEFT | wx.TOP, 8)

        # Encoding choice
        self.encoding_choice = wx.Choice(
            self,
            choices=[
                "UTF-8 (Unicode, recomendado)",
                "ISO-8859-1 (Latin-1)",
                "CP1252 (Windows)",
                "ASCII"
            ]
        )
        self.encoding_choice.SetName("Codificación de caracteres")
        self.encoding_choice.SetSelection(0)  # Default to UTF-8
        encoding_box_sizer.Add(self.encoding_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        sizer.Add(encoding_box_sizer, 0, wx.EXPAND | wx.ALL, 12)

        # === Output Filtering Section ===
        filter_box = wx.StaticBox(self, label="Filtrado de Salida")
        filter_box_sizer = wx.StaticBoxSizer(filter_box, wx.VERTICAL)

        # Filter long descriptions checkbox
        self.filter_descriptions_check = wx.CheckBox(
            self,
            label="Filtrar descripciones largas de rooms"
        )
        self.filter_descriptions_check.SetName("Filtrar descripciones largas")
        self.filter_descriptions_check.SetValue(True)  # Default enabled
        filter_box_sizer.Add(self.filter_descriptions_check, 0, wx.LEFT | wx.TOP | wx.RIGHT, 8)

        # Description length threshold
        length_label = wx.StaticText(self, label="Longitud máxima antes de filtrar (caracteres):")
        length_label.SetFont(label_font)
        filter_box_sizer.Add(length_label, 0, wx.LEFT | wx.TOP | wx.RIGHT, 8)

        self.max_description_length = wx.SpinCtrl(
            self,
            value="250",
            min=50,
            max=2000
        )
        self.max_description_length.SetName("Longitud máxima")
        filter_box_sizer.Add(self.max_description_length, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        sizer.Add(filter_box_sizer, 0, wx.EXPAND | wx.ALL, 12)

        # === Info text ===
        info_text = wx.StaticText(
            self,
            label="Codificación:\n"
                  "UTF-8: Compatible con caracteres internacionales\n"
                  "ISO-8859-1: Para MUDs con caracteres latinos\n"
                  "\n"
                  "Filtrado:\n"
                  "Activa para evitar spam al viajar rápido"
        )
        info_text.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        sizer.Add(info_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        # === Button row ===
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer()

        ok_btn = wx.Button(self, wx.ID_OK, "&Aceptar")
        ok_btn.SetMinSize((100, 32))
        button_sizer.Add(ok_btn, 0, wx.LEFT, 8)

        cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancelar")
        cancel_btn.SetMinSize((100, 32))
        button_sizer.Add(cancel_btn, 0, wx.LEFT, 8)

        sizer.Add(button_sizer, 0, wx.EXPAND | wx.RIGHT | wx.BOTTOM, 12)

        self.SetSizer(sizer)

    def _load_config(self):
        """Load current configuration from file."""
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

                # Load encoding
                encoding = config.get('connection', {}).get('encoding', 'utf-8').upper()
                encoding_map = {
                    'UTF-8': 0,
                    'ISO-8859-1': 1,
                    'CP1252': 2,
                    'ASCII': 3
                }
                index = encoding_map.get(encoding, 0)
                self.encoding_choice.SetSelection(index)

                # Load output filtering settings
                filter_config = config.get('output_filter', {})
                self.filter_descriptions_check.SetValue(filter_config.get('filter_long_descriptions', True))
                self.max_description_length.SetValue(filter_config.get('max_description_length', 250))
        except Exception:
            pass

    def _save_config(self):
        """Save preferences to config file."""
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Map choice index back to encoding name
            encoding_names = ['utf-8', 'iso-8859-1', 'cp1252', 'ascii']
            selected_index = self.encoding_choice.GetSelection()
            new_encoding = encoding_names[selected_index]

            # Update connection settings
            if 'connection' not in config:
                config['connection'] = {}
            config['connection']['encoding'] = new_encoding

            # Update output filtering settings
            if 'output_filter' not in config:
                config['output_filter'] = {}
            config['output_filter']['filter_long_descriptions'] = self.filter_descriptions_check.GetValue()
            config['output_filter']['max_description_length'] = self.max_description_length.GetValue()

            # Save back to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            wx.MessageBox(f"Error guardando configuración: {e}", "Error")

    def get_selected_encoding(self):
        """Get selected encoding as uppercase string (UTF-8, ISO-8859-1, etc.)."""
        encoding_names = ['UTF-8', 'ISO-8859-1', 'CP1252', 'ASCII']
        return encoding_names[self.encoding_choice.GetSelection()]

    def get_filter_long_descriptions(self):
        """Get whether to filter long descriptions."""
        return self.filter_descriptions_check.GetValue()

    def get_max_description_length(self):
        """Get maximum description length threshold."""
        return self.max_description_length.GetValue()

    def ShowModal(self):
        """Show dialog and return result."""
        result = super().ShowModal()

        if result == wx.ID_OK:
            self._save_config()

        return result

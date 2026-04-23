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
        sizer.SetMinSize((480, 330))

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

        # === Info text ===
        info_text = wx.StaticText(
            self,
            label="UTF-8: Compatible con caracteres internacionales\n"
                  "ISO-8859-1: Para MUDs con caracteres latinos\n"
                  "CP1252: Windows extended ASCII\n"
                  "ASCII: Solo caracteres básicos"
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
                encoding = config.get('connection', {}).get('encoding', 'utf-8').upper()

                # Map encoding name to choice index
                encoding_map = {
                    'UTF-8': 0,
                    'ISO-8859-1': 1,
                    'CP1252': 2,
                    'ASCII': 3
                }
                index = encoding_map.get(encoding, 0)
                self.encoding_choice.SetSelection(index)
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

            # Update config
            if 'connection' not in config:
                config['connection'] = {}
            config['connection']['encoding'] = new_encoding

            # Save back to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            wx.MessageBox(f"Error guardando configuración: {e}", "Error")

    def get_selected_encoding(self):
        """Get selected encoding as uppercase string (UTF-8, ISO-8859-1, etc.)."""
        encoding_names = ['UTF-8', 'ISO-8859-1', 'CP1252', 'ASCII']
        return encoding_names[self.encoding_choice.GetSelection()]

    def ShowModal(self):
        """Show dialog and return result."""
        result = super().ShowModal()

        if result == wx.ID_OK:
            self._save_config()

        return result

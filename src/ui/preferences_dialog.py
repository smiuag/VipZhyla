"""
Preferences Dialog - User configurable settings for VipZhyla
"""

import wx
import json
from pathlib import Path
from client.mud_parser import ChannelType
from models.channel_config import ChannelConfig


class PreferencesDialog(wx.Dialog):
    """Dialog for user preferences (encoding, audio, channels, filtering)."""

    def __init__(self, parent, current_encoding="UTF-8", channel_config: ChannelConfig = None):
        """Initialize preferences dialog.

        Args:
            parent: Parent window
            current_encoding: Current character encoding (default: UTF-8)
            channel_config: ChannelConfig instance for muting settings
        """
        super().__init__(parent, title="Preferencias", size=(600, 450))
        self.current_encoding = current_encoding
        self.channel_config = channel_config or ChannelConfig()
        self.config_path = Path("src/config/mud_config.json")

        self._build_ui()
        self._load_config()
        self.Centre()

    def _build_ui(self):
        """Build preferences dialog UI with notebook tabs."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.SetMinSize((600, 450))

        # Notebook with 4 tabs
        self.notebook = wx.Notebook(self)

        self.connection_panel = self._build_connection_tab()
        self.channels_panel = self._build_channels_tab()
        self.audio_panel = self._build_audio_tab()
        self.filters_panel = self._build_filters_tab()

        self.notebook.AddPage(self.connection_panel, "Conexión")
        self.notebook.AddPage(self.channels_panel, "Canales")
        self.notebook.AddPage(self.audio_panel, "Audio")
        self.notebook.AddPage(self.filters_panel, "Filtros")

        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self, wx.ID_OK, "&Aceptar")
        cancel_btn = wx.Button(self, wx.ID_CANCEL, "&Cancelar")
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(ok_btn, 0, wx.RIGHT, 5)
        btn_sizer.Add(cancel_btn, 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self._on_ok, ok_btn)
        self.Bind(wx.EVT_BUTTON, self._on_cancel, cancel_btn)

    def _build_connection_tab(self) -> wx.Panel:
        """Build connection settings tab."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Encoding section
        enc_label = wx.StaticText(panel, label="Codificación de Caracteres:")
        enc_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(enc_label, 0, wx.LEFT | wx.TOP, 15)

        self.encoding_choice = wx.Choice(
            panel,
            choices=[
                "UTF-8 (Unicode, recomendado)",
                "ISO-8859-1 (Latin-1)",
                "CP1252 (Windows)",
                "ASCII"
            ]
        )
        self.encoding_choice.SetName("Codificación de caracteres")
        self.encoding_choice.SetSelection(0)
        sizer.Add(self.encoding_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 15)

        sizer.AddStretchSpacer()

        panel.SetSizer(sizer)
        return panel

    def _build_channels_tab(self) -> wx.Panel:
        """Build channel muting settings tab."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(panel, label="Silenciar canales (no anuncia por TTS):")
        label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(label, 0, wx.LEFT | wx.TOP, 15)

        # Create checkbox for each channel
        self.channel_checks = {}
        for channel_enum in ChannelType:
            channel_value = channel_enum.value
            is_muted = self.channel_config.is_muted(channel_enum)

            check = wx.CheckBox(panel, label=f"{channel_value.capitalize()}")
            check.SetValue(is_muted)
            check.SetName(f"Silenciar {channel_value}")
            self.channel_checks[channel_value] = check
            sizer.Add(check, 0, wx.LEFT | wx.TOP, 20)

        # Buttons for quick actions
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        mute_all_btn = wx.Button(panel, label="Silenciar todo")
        unmute_all_btn = wx.Button(panel, label="Activar todo")
        mute_all_btn.Bind(wx.EVT_BUTTON, self._on_mute_all)
        unmute_all_btn.Bind(wx.EVT_BUTTON, self._on_unmute_all)
        btn_sizer.Add(mute_all_btn, 0, wx.RIGHT, 5)
        btn_sizer.Add(unmute_all_btn, 0)

        sizer.AddStretchSpacer()
        sizer.Add(btn_sizer, 0, wx.LEFT | wx.TOP, 15)

        panel.SetSizer(sizer)
        return panel

    def _build_audio_tab(self) -> wx.Panel:
        """Build audio settings tab."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # TTS Speed
        speed_label = wx.StaticText(panel, label="Velocidad de Voz (TTS):")
        speed_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(speed_label, 0, wx.LEFT | wx.TOP, 15)

        speed_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.speed_slider = wx.Slider(panel, value=50, minValue=20, maxValue=100, style=wx.SL_HORIZONTAL)
        self.speed_slider.SetName("Velocidad de voz")
        self.speed_label = wx.StaticText(panel, label="50%")
        self.speed_slider.Bind(wx.EVT_SLIDER, self._on_speed_changed)
        speed_sizer.Add(self.speed_slider, 1, wx.RIGHT, 10)
        speed_sizer.Add(self.speed_label, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(speed_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 15)

        # Volume
        vol_label = wx.StaticText(panel, label="Volumen de Audio:")
        vol_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(vol_label, 0, wx.LEFT | wx.TOP, 15)

        vol_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.volume_slider = wx.Slider(panel, value=80, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
        self.volume_slider.SetName("Volumen de audio")
        self.vol_label = wx.StaticText(panel, label="80%")
        self.volume_slider.Bind(wx.EVT_SLIDER, self._on_volume_changed)
        vol_sizer.Add(self.volume_slider, 1, wx.RIGHT, 10)
        vol_sizer.Add(self.vol_label, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(vol_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 15)

        # Verbosity
        verb_label = wx.StaticText(panel, label="Verbosidad:")
        verb_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(verb_label, 0, wx.LEFT | wx.TOP, 15)

        self.verbosity_choice = wx.Choice(panel, choices=["Silencioso", "Mínimo", "Normal", "Verboso"])
        self.verbosity_choice.SetSelection(2)  # Default: Normal
        self.verbosity_choice.SetName("Nivel de verbosidad")
        sizer.Add(self.verbosity_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 15)

        sizer.AddStretchSpacer()

        panel.SetSizer(sizer)
        return panel

    def _build_filters_tab(self) -> wx.Panel:
        """Build output filtering settings tab."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Filter long descriptions checkbox
        self.filter_descriptions_check = wx.CheckBox(
            panel,
            label="Filtrar descripciones largas de rooms"
        )
        self.filter_descriptions_check.SetName("Filtrar descripciones largas")
        self.filter_descriptions_check.SetValue(True)
        sizer.Add(self.filter_descriptions_check, 0, wx.LEFT | wx.TOP, 15)

        # Description length threshold
        length_label = wx.StaticText(panel, label="Longitud máxima antes de filtrar (caracteres):")
        length_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(length_label, 0, wx.LEFT | wx.TOP, 20)

        self.max_description_length = wx.SpinCtrl(
            panel,
            value=250,
            min=50,
            max=2000
        )
        self.max_description_length.SetName("Longitud máxima de descripción")
        sizer.Add(self.max_description_length, 0, wx.LEFT | wx.RIGHT, 20)

        sizer.AddStretchSpacer()

        panel.SetSizer(sizer)
        return panel

    def _on_speed_changed(self, event):
        """Update speed label."""
        value = self.speed_slider.GetValue()
        self.speed_label.SetLabel(f"{value}%")

    def _on_volume_changed(self, event):
        """Update volume label."""
        value = self.volume_slider.GetValue()
        self.vol_label.SetLabel(f"{value}%")

    def _on_mute_all(self, event):
        """Mute all channels."""
        for check in self.channel_checks.values():
            check.SetValue(True)

    def _on_unmute_all(self, event):
        """Unmute all channels."""
        for check in self.channel_checks.values():
            check.SetValue(False)

    def _on_ok(self, event):
        """Save preferences and close."""
        self._save_config()
        self.EndModal(wx.ID_OK)

    def _on_cancel(self, event):
        """Close without saving."""
        self.EndModal(wx.ID_CANCEL)

    def _load_config(self) -> None:
        """Load existing preferences from JSON."""
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Connection section
            conn_config = config.get('connection', {})
            encoding_str = conn_config.get('encoding', 'UTF-8')
            if 'UTF-8' in encoding_str or 'utf' in encoding_str.lower():
                self.encoding_choice.SetSelection(0)
            elif 'ISO-8859-1' in encoding_str or '8859' in encoding_str:
                self.encoding_choice.SetSelection(1)
            elif 'CP1252' in encoding_str or 'windows' in encoding_str.lower():
                self.encoding_choice.SetSelection(2)
            elif 'ASCII' in encoding_str:
                self.encoding_choice.SetSelection(3)

            # Channel muting section
            channel_config = config.get('channel_muting', {})
            for channel_value, check in self.channel_checks.items():
                is_muted = channel_config.get(channel_value, False)
                check.SetValue(is_muted)

            # Audio section
            audio_config = config.get('audio_settings', {})
            self.speed_slider.SetValue(audio_config.get('tts_speed', 50))
            self.speed_label.SetLabel(f"{audio_config.get('tts_speed', 50)}%")
            self.volume_slider.SetValue(audio_config.get('audio_volume', 80))
            self.vol_label.SetLabel(f"{audio_config.get('audio_volume', 80)}%")

            verbosity_map = {'silent': 0, 'minimal': 1, 'normal': 2, 'verbose': 3}
            verb = audio_config.get('verbosity', 'normal').lower()
            self.verbosity_choice.SetSelection(verbosity_map.get(verb, 2))

            # Filters section
            filter_config = config.get('output_filter', {})
            self.filter_descriptions_check.SetValue(filter_config.get('filter_long_descriptions', True))
            self.max_description_length.SetValue(filter_config.get('max_description_length', 250))

        except (json.JSONDecodeError, IOError, KeyError):
            pass  # File corrupted or missing; use defaults

    def _save_config(self) -> None:
        """Save preferences to JSON."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config to preserve other sections
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            config = {}

        # Update sections
        encoding_choices = ["UTF-8", "ISO-8859-1", "CP1252", "ASCII"]
        config['connection'] = {
            'encoding': encoding_choices[self.encoding_choice.GetSelection()]
        }

        config['channel_muting'] = {
            channel_value: check.GetValue()
            for channel_value, check in self.channel_checks.items()
        }

        verbosity_choices = ['silent', 'minimal', 'normal', 'verbose']
        config['audio_settings'] = {
            'tts_speed': self.speed_slider.GetValue(),
            'audio_volume': self.volume_slider.GetValue(),
            'verbosity': verbosity_choices[self.verbosity_choice.GetSelection()]
        }

        config['output_filter'] = {
            'filter_long_descriptions': self.filter_descriptions_check.GetValue(),
            'max_description_length': self.max_description_length.GetValue()
        }

        # Apply channel muting to ChannelConfig instance
        for channel_enum in ChannelType:
            channel_value = channel_enum.value
            if self.channel_checks[channel_value].GetValue():
                self.channel_config.set_muted(channel_enum, True)
            else:
                self.channel_config.set_muted(channel_enum, False)

        # Save JSON
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def get_selected_encoding(self) -> str:
        """Get selected encoding."""
        choices = ["UTF-8", "ISO-8859-1", "CP1252", "ASCII"]
        return choices[self.encoding_choice.GetSelection()]

    def get_filter_long_descriptions(self) -> bool:
        """Get whether to filter long descriptions."""
        return self.filter_descriptions_check.GetValue()

    def get_max_description_length(self) -> int:
        """Get max description length before filtering."""
        return self.max_description_length.GetValue()

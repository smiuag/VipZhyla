"""
BlockList Dialog - UI for managing blocked players, keywords, and channels.
"""

import wx
from models.blocklist import BlockList


class BlocklistDialog(wx.Dialog):
    """Dialog for managing blocked players, keywords, and channels."""

    def __init__(self, parent, blocklist: BlockList):
        """Initialize blocklist dialog.

        Args:
            parent: Parent window
            blocklist: BlockList instance to manage
        """
        super().__init__(parent, title="Blocklist - Bloqueados", size=(550, 450))
        self.blocklist = blocklist
        self.Centre()

        self._build_ui()
        self._load_lists()

    def _build_ui(self) -> None:
        """Build dialog UI with notebook tabs."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Notebook with 3 tabs
        self.notebook = wx.Notebook(self)
        self.player_panel = self._build_player_tab()
        self.keyword_panel = self._build_keyword_tab()
        self.channel_panel = self._build_channel_tab()

        self.notebook.AddPage(self.player_panel, "Jugadores")
        self.notebook.AddPage(self.keyword_panel, "Palabras clave")
        self.notebook.AddPage(self.channel_panel, "Canales")

        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 10)

        # Stats label
        self.stats_label = wx.StaticText(
            self,
            label=self._format_stats()
        )
        stats_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        self.stats_label.SetFont(stats_font)
        sizer.Add(self.stats_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        clear_btn = wx.Button(self, label="Limpiar todo")
        clear_btn.SetName("Clear All Blocks")
        clear_btn.Bind(wx.EVT_BUTTON, self._on_clear_all)
        close_btn = wx.Button(self, wx.ID_CLOSE, "&Cerrar")
        close_btn.Bind(wx.EVT_BUTTON, self._on_close)

        btn_sizer.Add(clear_btn, 0, wx.RIGHT, 5)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(close_btn, 0)

        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(sizer)

    def _build_player_tab(self) -> wx.Panel:
        """Build players tab."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Label
        label = wx.StaticText(panel, label="Nombres de jugadores bloqueados:")
        sizer.Add(label, 0, wx.LEFT | wx.TOP, 10)

        # Input + Add button
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.player_input = wx.TextCtrl(panel, size=(300, -1))
        self.player_input.SetName("Nombre de jugador")
        add_btn = wx.Button(panel, label="&Añadir")
        add_btn.SetName("Add Player to Blocklist")
        add_btn.Bind(wx.EVT_BUTTON, self._on_add_player)
        input_sizer.Add(self.player_input, 1, wx.RIGHT, 5)
        input_sizer.Add(add_btn, 0)
        sizer.Add(input_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # List
        self.player_list = wx.ListBox(panel, style=wx.LB_SINGLE)
        self.player_list.SetName("Lista de jugadores bloqueados")
        sizer.Add(self.player_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Remove button
        remove_btn = wx.Button(panel, label="&Quitar seleccionado")
        remove_btn.SetName("Remove Player from Blocklist")
        remove_btn.Bind(wx.EVT_BUTTON, self._on_remove_player)
        sizer.Add(remove_btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(sizer)
        return panel

    def _build_keyword_tab(self) -> wx.Panel:
        """Build keywords tab."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(panel, label="Palabras clave a bloquear:")
        sizer.Add(label, 0, wx.LEFT | wx.TOP, 10)

        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.keyword_input = wx.TextCtrl(panel, size=(300, -1))
        self.keyword_input.SetName("Palabra clave")
        add_btn = wx.Button(panel, label="&Añadir")
        add_btn.SetName("Add Keyword to Blocklist")
        add_btn.Bind(wx.EVT_BUTTON, self._on_add_keyword)
        input_sizer.Add(self.keyword_input, 1, wx.RIGHT, 5)
        input_sizer.Add(add_btn, 0)
        sizer.Add(input_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.keyword_list = wx.ListBox(panel, style=wx.LB_SINGLE)
        self.keyword_list.SetName("Lista de palabras clave bloqueadas")
        sizer.Add(self.keyword_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        remove_btn = wx.Button(panel, label="&Quitar seleccionado")
        remove_btn.SetName("Remove Keyword from Blocklist")
        remove_btn.Bind(wx.EVT_BUTTON, self._on_remove_keyword)
        sizer.Add(remove_btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(sizer)
        return panel

    def _build_channel_tab(self) -> wx.Panel:
        """Build channels tab."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(panel, label="Canales bloqueados:")
        sizer.Add(label, 0, wx.LEFT | wx.TOP, 10)

        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.channel_input = wx.TextCtrl(panel, size=(300, -1))
        self.channel_input.SetName("Canal")
        add_btn = wx.Button(panel, label="&Añadir")
        add_btn.SetName("Add Channel to Blocklist")
        add_btn.Bind(wx.EVT_BUTTON, self._on_add_channel)
        input_sizer.Add(self.channel_input, 1, wx.RIGHT, 5)
        input_sizer.Add(add_btn, 0)
        sizer.Add(input_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.channel_list = wx.ListBox(panel, style=wx.LB_SINGLE)
        self.channel_list.SetName("Lista de canales bloqueados")
        sizer.Add(self.channel_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        remove_btn = wx.Button(panel, label="&Quitar seleccionado")
        remove_btn.SetName("Remove Channel from Blocklist")
        remove_btn.Bind(wx.EVT_BUTTON, self._on_remove_channel)
        sizer.Add(remove_btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(sizer)
        return panel

    def _load_lists(self) -> None:
        """Load blocklist items into UI lists."""
        for player in sorted(self.blocklist.blocked_players):
            self.player_list.Append(player)

        for keyword in sorted(self.blocklist.blocked_keywords):
            self.keyword_list.Append(keyword)

        for channel in sorted(self.blocklist.blocked_channels):
            self.channel_list.Append(channel)

    def _on_add_player(self, event):
        """Add player to blocklist."""
        name = self.player_input.GetValue().strip()
        if not name:
            return

        self.blocklist.add_player(name)
        self.player_list.Append(name.lower())
        self.player_input.SetValue("")
        self._update_stats()

    def _on_remove_player(self, event):
        """Remove selected player from blocklist."""
        sel = self.player_list.GetSelection()
        if sel != wx.NOT_FOUND:
            name = self.player_list.GetString(sel)
            self.blocklist.remove_player(name)
            self.player_list.Delete(sel)
            self._update_stats()

    def _on_add_keyword(self, event):
        """Add keyword to blocklist."""
        kw = self.keyword_input.GetValue().strip()
        if not kw:
            return

        self.blocklist.add_keyword(kw)
        self.keyword_list.Append(kw.lower())
        self.keyword_input.SetValue("")
        self._update_stats()

    def _on_remove_keyword(self, event):
        """Remove selected keyword from blocklist."""
        sel = self.keyword_list.GetSelection()
        if sel != wx.NOT_FOUND:
            kw = self.keyword_list.GetString(sel)
            self.blocklist.remove_keyword(kw)
            self.keyword_list.Delete(sel)
            self._update_stats()

    def _on_add_channel(self, event):
        """Add channel to blocklist."""
        ch = self.channel_input.GetValue().strip()
        if not ch:
            return

        self.blocklist.add_channel(ch)
        self.channel_list.Append(ch.lower())
        self.channel_input.SetValue("")
        self._update_stats()

    def _on_remove_channel(self, event):
        """Remove selected channel from blocklist."""
        sel = self.channel_list.GetSelection()
        if sel != wx.NOT_FOUND:
            ch = self.channel_list.GetString(sel)
            self.blocklist.remove_channel(ch)
            self.channel_list.Delete(sel)
            self._update_stats()

    def _on_clear_all(self, event):
        """Clear all blocks after confirmation."""
        dlg = wx.MessageDialog(
            self,
            "Esto eliminará todos los bloques. Continuar?",
            "Confirmar limpiar todo",
            wx.YES_NO | wx.ICON_WARNING
        )

        if dlg.ShowModal() == wx.ID_YES:
            self.blocklist.clear_all()
            self.player_list.Clear()
            self.keyword_list.Clear()
            self.channel_list.Clear()
            self._update_stats()

        dlg.Destroy()

    def _on_close(self, event):
        """Close dialog."""
        self.EndModal(wx.ID_CLOSE)

    def _format_stats(self) -> str:
        """Format statistics string."""
        stats = self.blocklist.get_stats()
        if stats['total'] == 0:
            return "No hay bloques activos"

        parts = []
        if stats['players'] > 0:
            parts.append(f"{stats['players']} jugador{'es' if stats['players'] != 1 else ''}")
        if stats['keywords'] > 0:
            parts.append(f"{stats['keywords']} palabra{'s' if stats['keywords'] != 1 else ''}")
        if stats['channels'] > 0:
            parts.append(f"{stats['channels']} canal{'es' if stats['channels'] != 1 else ''}")

        return f"Bloqueando: {', '.join(parts)}"

    def _update_stats(self) -> None:
        """Update stats label."""
        self.stats_label.SetLabel(self._format_stats())


def show_blocklist_dialog(parent, blocklist: BlockList) -> None:
    """Show blocklist dialog (modal).

    Args:
        parent: Parent window
        blocklist: BlockList instance
    """
    dlg = BlocklistDialog(parent, blocklist)
    dlg.ShowModal()
    dlg.Destroy()

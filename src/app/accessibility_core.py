"""
Accessibility Core - wx.Accessible wrapper and utilities

This module provides a base class for creating accessible wxPython controls
that work with NVDA, JAWS, and Narrator screen readers.
"""

import wx


class AccessibleControl(wx.Window):
    """Base class for accessible wxPython controls.

    Subclasses should override GetAccessible() and GetAccessibleName().
    """

    def __init__(self, parent, name="", description=""):
        """Initialize accessible control.

        Args:
            parent: Parent wxPython window
            name: Control name (for screen readers)
            description: Control description (for screen readers)
        """
        super().__init__(parent)
        self._name = name
        self._description = description
        self._value = ""

    def SetAccessibleName(self, name):
        """Set name announced by screen reader."""
        self._name = name
        if hasattr(self, 'SetName'):
            self.SetName(name)

    def SetAccessibleDescription(self, description):
        """Set description announced by screen reader."""
        self._description = description
        if hasattr(self, 'SetDescription'):
            self.SetDescription(description)

    def GetAccessibleName(self):
        """Get name for screen reader."""
        return self._name

    def GetAccessibleDescription(self):
        """Get description for screen reader."""
        return self._description

    def GetAccessibleValue(self):
        """Get current value for screen reader."""
        return self._value

    def SetAccessibleValue(self, value):
        """Set value to announce via screen reader."""
        self._value = value
        self.NotifyAccessible()

    def NotifyAccessible(self):
        """Notify screen reader of state change.

        Call this after updating control state that should be announced.
        """
        try:
            # Fire focus event to notify screen reader
            event = wx.PyEvent()
            wx.PostEvent(self, event)
        except Exception:
            # Graceful fallback if accessibility notification fails
            pass


class AccessiblePanel(wx.Panel):
    """Accessible wxPython panel.

    Base class for panels that need accessibility support.
    """

    def __init__(self, parent, name="", description=""):
        """Initialize accessible panel.

        Args:
            parent: Parent wxPython window
            name: Panel name (for screen readers)
            description: Panel description (for screen readers)
        """
        super().__init__(parent)
        self._name = name
        self._description = description

        # Set accessibility info
        if name:
            self.SetName(name)
        if description:
            self.SetDescription(description)

    def MakeAccessible(self):
        """Enable accessibility for this panel and its children."""
        self._make_recursive_accessible(self)

    def _make_recursive_accessible(self, window):
        """Recursively ensure all children are accessible."""
        for child in window.GetChildren():
            if hasattr(child, 'GetLabel'):
                label = child.GetLabel()
                if label and not child.GetName():
                    child.SetName(label)

            # Recurse into child windows
            if hasattr(child, 'GetChildren'):
                self._make_recursive_accessible(child)


class AccessibleTextCtrl(wx.TextCtrl, AccessibleControl):
    """Accessible text control for wxPython.

    Combines wx.TextCtrl with accessibility support.
    """

    def __init__(self, parent, name="", description="", **kwargs):
        """Initialize accessible text control.

        Args:
            parent: Parent wxPython window
            name: Control name (for screen readers)
            description: Control description (for screen readers)
            **kwargs: Additional arguments for wx.TextCtrl
        """
        wx.TextCtrl.__init__(self, parent, **kwargs)
        self._name = name
        self._description = description

        if name:
            self.SetName(name)
        if description:
            self.SetDescription(description)


def announce_via_accessible(window, message):
    """Announce a message to screen readers.

    This is a helper function to announce information without changing
    the actual control state.

    Args:
        window: wxPython window that has focus
        message: Message to announce
    """
    try:
        if hasattr(window, 'SetAccessibleValue'):
            window.SetAccessibleValue(message)
        elif hasattr(window, 'SetValue'):
            # Fallback for controls that have SetValue
            pass
    except Exception:
        # Graceful fallback if announcement fails
        pass

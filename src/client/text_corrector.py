"""
Text Corrector - Normalize MUD output for consistent display and TTS.

Implements VipMud's Corrector.set functionality:
- Normalize accented characters (é → e, á → a, etc.)
- Fix double spaces and whitespace issues
- Remove problematic characters
- Normalize punctuation
- Ensure consistent encoding

This prevents issues like "sensaciÃ³n" appearing as "sensación"
(which happens when UTF-8 bytes are interpreted as Latin-1).
"""

import unicodedata
import re


class TextCorrector:
    """Normalize and correct MUD text output."""

    # Mapping of accented characters to ASCII equivalents
    # Useful for screen readers that have trouble with accents
    ACCENT_MAP = {
        'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a', 'ã': 'a',
        'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i',
        'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u',
        'ñ': 'n',
        'ç': 'c',
        'Á': 'A', 'À': 'A', 'Ä': 'A', 'Â': 'A', 'Ã': 'A',
        'É': 'E', 'È': 'E', 'Ë': 'E', 'Ê': 'E',
        'Í': 'I', 'Ì': 'I', 'Ï': 'I', 'Î': 'I',
        'Ó': 'O', 'Ò': 'O', 'Ö': 'O', 'Ô': 'O', 'Õ': 'O',
        'Ú': 'U', 'Ù': 'U', 'Ü': 'U', 'Û': 'U',
        'Ñ': 'N',
        'Ç': 'C',
    }

    # Characters to remove entirely
    REMOVE_CHARS = [
        '\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07',
        '\x08', '\x0b', '\x0c', '\x0e', '\x0f',  # Control characters
        '\xa0',  # Non-breaking space
    ]

    def __init__(self, keep_accents=True):
        """
        Initialize text corrector.

        Args:
            keep_accents (bool): If True, keep accented characters.
                                If False, convert to ASCII equivalents.
                                Default: True (keep accents)
        """
        self.keep_accents = keep_accents

    def correct(self, text):
        """
        Correct and normalize text.

        Args:
            text (str): Raw text from MUD

        Returns:
            str: Corrected text
        """
        if not text:
            return text

        # Step 1: Remove control characters
        text = self._remove_control_chars(text)

        # Step 2: Fix common encoding issues (UTF-8 double-encoded as Latin-1)
        text = self._fix_encoding_issues(text)

        # Step 3: Normalize whitespace
        text = self._normalize_whitespace(text)

        # Step 4: Normalize accents (if requested)
        if not self.keep_accents:
            text = self._remove_accents(text)

        # Step 5: Normalize punctuation
        text = self._normalize_punctuation(text)

        return text

    def _remove_control_chars(self, text):
        """Remove problematic control characters."""
        for char in self.REMOVE_CHARS:
            text = text.replace(char, '')
        return text

    def _fix_encoding_issues(self, text):
        """
        Fix common UTF-8 double-encoding issues.

        Example: "sensaciÃ³n" (UTF-8 bytes interpreted as Latin-1)
                 → "sensación" (correct UTF-8)
        """
        # Try to detect and fix UTF-8 encoded as Latin-1
        try:
            # If text contains typical double-encoded patterns, try to fix
            if 'Ã' in text or 'â' in text or 'Â' in text:
                # Attempt to encode as Latin-1 then decode as UTF-8
                try:
                    fixed = text.encode('latin-1').decode('utf-8', errors='ignore')
                    # Only use if it actually improved the text
                    if 'Ã' not in fixed:
                        return fixed
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
        except Exception:
            pass

        return text

    def _normalize_whitespace(self, text):
        """
        Normalize whitespace:
        - Remove leading/trailing spaces
        - Convert multiple spaces to single space
        - Normalize line endings
        """
        # Normalize line endings (CRLF → LF)
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Convert multiple spaces to single space
        text = re.sub(r' +', ' ', text)

        # Remove trailing spaces from each line
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        text = '\n'.join(lines)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def _remove_accents(self, text):
        """
        Convert accented characters to ASCII equivalents.

        Example: "sensación" → "sensacion"
        """
        result = []
        for char in text:
            if char in self.ACCENT_MAP:
                result.append(self.ACCENT_MAP[char])
            else:
                result.append(char)
        return ''.join(result)

    def _normalize_punctuation(self, text):
        """
        Normalize punctuation:
        - Fix spacing around punctuation
        - Normalize quotes
        """
        # Fix spacing before punctuation (remove space before . , ! ?)
        text = re.sub(r'\s+([.,:!?;])', r'\1', text)

        # Normalize different quote styles to standard quotes
        text = text.replace('"', '"').replace('"', '"')  # Smart quotes → regular
        text = text.replace(''', "'").replace(''', "'")  # Smart apostrophes → regular

        # Fix spacing after punctuation (ensure single space)
        text = re.sub(r'([.,:!?;])\s+', r'\1 ', text)

        return text

    def correct_channel_message(self, channel, text):
        """
        Correct message from specific channel.

        Can apply channel-specific corrections in future.

        Args:
            channel (str): Channel type (e.g., "bando", "telepathy")
            text (str): Message text

        Returns:
            str: Corrected text
        """
        # Apply general correction
        text = self.correct(text)

        # Channel-specific corrections could go here
        # E.g., remove channel prefix from captured text

        return text

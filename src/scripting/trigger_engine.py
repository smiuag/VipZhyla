"""
Trigger pattern engine for Lua scripts.

Converts MushClient trigger syntax (wildcards) and regex patterns to Python regex.
Handles trigger matching against MUD output text.
"""

import re
import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TriggerPattern:
    """Compiled trigger pattern."""
    original: str
    regex: re.Pattern
    is_regex: bool
    case_insensitive: bool


class TriggerEngine:
    """Compiles and matches trigger patterns."""

    def __init__(self):
        """Initialize trigger engine."""
        self.pattern_cache: dict[str, TriggerPattern] = {}

    def compile_pattern(self, pattern: str, is_regex: bool = False,
                       case_insensitive: bool = True) -> TriggerPattern:
        """
        Compile trigger pattern to regex.

        Args:
            pattern: MushClient pattern or regex pattern
            is_regex: If True, pattern is already regex syntax
            case_insensitive: Ignore case in matching

        Returns:
            Compiled TriggerPattern

        Raises:
            re.error: If regex compilation fails
        """
        # Check cache first
        cache_key = f"{pattern}|{is_regex}|{case_insensitive}"
        if cache_key in self.pattern_cache:
            return self.pattern_cache[cache_key]

        if is_regex:
            # Pattern is already regex syntax
            regex_pattern = pattern
        else:
            # Convert MushClient wildcards to regex
            regex_pattern = self._convert_mushclient_pattern(pattern)

        # Compile regex
        flags = re.IGNORECASE if case_insensitive else 0
        try:
            regex = re.compile(regex_pattern, flags)
        except re.error as e:
            logger.error(f"Failed to compile pattern '{pattern}': {e}")
            raise

        trigger_pattern = TriggerPattern(
            original=pattern,
            regex=regex,
            is_regex=is_regex,
            case_insensitive=case_insensitive
        )

        self.pattern_cache[cache_key] = trigger_pattern
        logger.debug(f"Compiled trigger pattern: {pattern}")
        return trigger_pattern

    def match(self, pattern: TriggerPattern, text: str) -> bool:
        """
        Check if text matches compiled pattern.

        Args:
            pattern: Compiled TriggerPattern
            text: Text to match against

        Returns:
            True if text matches pattern
        """
        return bool(pattern.regex.search(text))

    def extract_captures(self, pattern: TriggerPattern, text: str) -> List[str]:
        """
        Extract capture groups from matched text.

        Args:
            pattern: Compiled TriggerPattern
            text: Text to extract from

        Returns:
            List of captured groups (empty if no match or no groups)
        """
        match = pattern.regex.search(text)
        if match:
            return list(match.groups())
        return []

    def _convert_mushclient_pattern(self, pattern: str) -> str:
        """
        Convert MushClient trigger pattern syntax to regex.

        MushClient patterns:
        - `*` matches any characters (greedy)
        - `[*]` matches word in brackets (any text)
        - `%0`, `%1`, etc. are positional arguments (converted to capture groups)

        Example:
            "You are in *." → "You are in (.*)\\."
            "[*] empieza a atacarte" → "(.+) empieza a atacarte"
            "* te alcanza con *" → "(.*) te alcanza con (.*)"

        Args:
            pattern: MushClient pattern syntax

        Returns:
            Valid Python regex pattern
        """
        # Escape special regex characters except * and []
        # We'll handle * separately
        escaped = ""
        for i, char in enumerate(pattern):
            if char == '*':
                # Unbounded wildcard - will handle below
                escaped += '*WILD*'
            elif char == '[':
                # Bracketed pattern like [*] - match any chars inside
                if i + 1 < len(pattern) and pattern[i + 1] == '*':
                    if i + 2 < len(pattern) and pattern[i + 2] == ']':
                        escaped += '[*BRACE*]'
                    else:
                        escaped += char
                else:
                    escaped += char
            else:
                # Escape regex special chars
                if char in r'\.+?(){}|^$':
                    escaped += '\\' + char
                else:
                    escaped += char

        # Convert wildcards to capture groups
        # [*] → (.+?)  (non-greedy, matches inside brackets)
        result = escaped.replace('[*BRACE*]', '(.+?)')

        # * → (.*?) (non-greedy match of any characters)
        # But be careful not to match *WILD* we added above
        result = result.replace('*WILD*', '(.*?)')

        logger.debug(f"Converted MushClient pattern: {pattern} → {result}")
        return result

    def validate_pattern(self, pattern: str) -> Tuple[bool, Optional[str]]:
        """
        Validate pattern syntax.

        Args:
            pattern: Pattern to validate

        Returns:
            (is_valid, error_message)
        """
        try:
            self.compile_pattern(pattern)
            return (True, None)
        except re.error as e:
            return (False, str(e))
        except Exception as e:
            return (False, f"Unexpected error: {e}")

    def clear_cache(self):
        """Clear compiled pattern cache."""
        self.pattern_cache.clear()
        logger.debug("Trigger pattern cache cleared")


# Singleton instance for module-level use
_engine = TriggerEngine()


def compile_pattern(pattern: str, is_regex: bool = False,
                   case_insensitive: bool = True) -> TriggerPattern:
    """Module-level function to compile patterns."""
    return _engine.compile_pattern(pattern, is_regex, case_insensitive)


def match(pattern: TriggerPattern, text: str) -> bool:
    """Module-level function to match patterns."""
    return _engine.match(pattern, text)


def extract_captures(pattern: TriggerPattern, text: str) -> List[str]:
    """Module-level function to extract captures."""
    return _engine.extract_captures(pattern, text)

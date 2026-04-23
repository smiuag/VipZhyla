"""Configuration loader for MUD connection and system settings.

Loads mud_config.json and provides validated configuration objects
for connection, character, and automation settings.
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerConfig:
    """MUD server connection settings."""
    host: str
    port: int
    timeout: int = 30
    reconnect_attempts: int = 3
    reconnect_delay: int = 5


@dataclass
class CharacterConfig:
    """Player character settings."""
    name: str
    password: str
    classe: str = "Soldado"
    race: str = "Humano"


@dataclass
class ConnectionConfig:
    """Connection protocol settings."""
    encoding: str = "utf-8"
    line_ending: str = "\r\n"
    gmcp_enabled: bool = True
    telnet_negotiation: bool = True


@dataclass
class AutomationConfig:
    """Automation and trigger settings."""
    auto_load_triggers: bool = True
    triggers_file: str = "src/data/triggers.json"
    auto_start_timers: bool = True
    log_all_output: bool = False
    log_file: str = "mud_output.log"


@dataclass
class AccessibilityConfig:
    """Accessibility and audio settings."""
    tts_enabled: bool = True
    verbosity: str = "NORMAL"
    announce_connection: bool = True
    announce_disconnection: bool = True
    announce_errors: bool = True


@dataclass
class MudConfig:
    """Complete configuration for MUD connection and system."""
    server: ServerConfig
    character: CharacterConfig
    connection: ConnectionConfig
    automation: AutomationConfig
    accessibility: AccessibilityConfig

    @staticmethod
    def load(config_path: str = "src/config/mud_config.json") -> "MudConfig":
        """Load configuration from JSON file.

        Args:
            config_path: Path to mud_config.json

        Returns:
            MudConfig instance with validated settings

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If configuration is invalid
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {config_path}: {e}")

        # Validate required fields
        required_server_fields = ['host', 'port']
        required_char_fields = ['name', 'password']

        if 'server' not in data:
            raise ValueError("Missing 'server' configuration")
        if 'character' not in data:
            raise ValueError("Missing 'character' configuration")

        server_config = data.get('server', {})
        for field in required_server_fields:
            if field not in server_config:
                raise ValueError(f"Missing required field: server.{field}")

        char_config = data.get('character', {})
        for field in required_char_fields:
            if field not in char_config:
                raise ValueError(f"Missing required field: character.{field}")

        # Build configuration objects
        server = ServerConfig(
            host=server_config['host'],
            port=server_config['port'],
            timeout=server_config.get('timeout', 30),
            reconnect_attempts=server_config.get('reconnect_attempts', 3),
            reconnect_delay=server_config.get('reconnect_delay', 5)
        )

        character = CharacterConfig(
            name=char_config['name'],
            password=char_config['password'],
            classe=char_config.get('class', 'Soldado'),
            race=char_config.get('race', 'Humano')
        )

        conn_config = data.get('connection', {})
        connection = ConnectionConfig(
            encoding=conn_config.get('encoding', 'utf-8'),
            line_ending=conn_config.get('line_ending', '\r\n'),
            gmcp_enabled=conn_config.get('gmcp_enabled', True),
            telnet_negotiation=conn_config.get('telnet_negotiation', True)
        )

        auto_config = data.get('automation', {})
        automation = AutomationConfig(
            auto_load_triggers=auto_config.get('auto_load_triggers', True),
            triggers_file=auto_config.get('triggers_file', 'src/data/triggers.json'),
            auto_start_timers=auto_config.get('auto_start_timers', True),
            log_all_output=auto_config.get('log_all_output', False),
            log_file=auto_config.get('log_file', 'mud_output.log')
        )

        acc_config = data.get('accessibility', {})
        accessibility = AccessibilityConfig(
            tts_enabled=acc_config.get('tts_enabled', True),
            verbosity=acc_config.get('verbosity', 'NORMAL'),
            announce_connection=acc_config.get('announce_connection', True),
            announce_disconnection=acc_config.get('announce_disconnection', True),
            announce_errors=acc_config.get('announce_errors', True)
        )

        return MudConfig(
            server=server,
            character=character,
            connection=connection,
            automation=automation,
            accessibility=accessibility
        )

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate configuration for correctness.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.server.host:
            return False, "Server host cannot be empty"
        if self.server.port < 1 or self.server.port > 65535:
            return False, f"Invalid port number: {self.server.port}"
        if not self.character.name:
            return False, "Character name cannot be empty"
        if not self.character.password:
            return False, "Character password cannot be empty"
        if self.server.timeout < 1:
            return False, "Timeout must be at least 1 second"
        if self.accessibility.verbosity not in ["SILENT", "MINIMAL", "NORMAL", "VERBOSE", "DEBUG"]:
            return False, f"Invalid verbosity level: {self.accessibility.verbosity}"

        return True, None

    def is_configured(self) -> bool:
        """Check if configuration is properly configured (not using defaults).

        Returns:
            True if host/port/name/password are not default values
        """
        return (
            self.server.host != "localhost" or
            self.server.port != 4000 or
            self.character.name != "YourCharacter" or
            self.character.password != "your_password"
        )

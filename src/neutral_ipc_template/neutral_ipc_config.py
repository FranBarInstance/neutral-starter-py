"""
Configuration module for Neutral IPC client.
Reads configuration from /etc/neutral-ipc-cfg.json or uses default values.
neutral-ipc-cfg.json is the configuration file used by the IPC server.
https://github.com/FranBarInstance/neutral-ipc
"""

import json
import os


class NeutralIpcConfig:
    """
    Configuration class for Neutral IPC client.

    This class provides configuration values by reading from a JSON file
    at /etc/neutral-ipc-cfg.json. If the file doesn't exist or values are missing,
    default values are used.

    Attributes:
        HOST (str): Default host address (127.0.0.1)
        PORT (int): Default port number (4273)
        TIMEOUT (int): Default timeout in seconds (10)
        BUFFER_SIZE (int): Default buffer size in bytes (8192)
    """

    # Default values
    HOST = '127.0.0.1'
    PORT = 4273
    TIMEOUT = 10
    BUFFER_SIZE = 8192

    # The IPC server configuration file
    CONFIG_FILE = '/etc/neutral-ipc-cfg.json'

    @classmethod
    def load_config(cls):
        """
        Load configuration from JSON file if it exists.

        Returns:
            dict: Configuration dictionary from file, or empty dict if file
                  doesn't exist or is invalid.
        """
        if not os.path.exists(cls.CONFIG_FILE):
            return {}

        try:
            with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, PermissionError):
            return {}

    @classmethod
    def get_config_value(cls, config_dict, key, default_value):
        """
        Safely get a configuration value from dictionary.

        Args:
            config_dict (dict): Configuration dictionary
            key (str): Key to look up
            default_value: Default value to return if key is missing or invalid

        Returns:
            Configuration value or default if not found/invalid
        """
        value = config_dict.get(key)
        if value is None:
            return default_value

        # Type validation for specific keys
        if key == 'host' and isinstance(value, str):
            return value
        elif key in ['port', 'timeout', 'buffer_size'] and isinstance(value, int):
            return value

        return default_value

    @classmethod
    def get_host(cls):
        """Get configured host address."""
        config = cls.load_config()
        return cls.get_config_value(config, 'host', cls.HOST)

    @classmethod
    def get_port(cls):
        """Get configured port number."""
        config = cls.load_config()
        return cls.get_config_value(config, 'port', cls.PORT)

    @classmethod
    def get_timeout(cls):
        """Get configured timeout value."""
        config = cls.load_config()
        return cls.get_config_value(config, 'timeout', cls.TIMEOUT)

    @classmethod
    def get_buffer_size(cls):
        """Get configured buffer size."""
        config = cls.load_config()
        return cls.get_config_value(config, 'buffer_size', cls.BUFFER_SIZE)


# Set module-level variables with appropriate values using public methods
HOST = NeutralIpcConfig.get_host()
PORT = NeutralIpcConfig.get_port()
TIMEOUT = NeutralIpcConfig.get_timeout()
BUFFER_SIZE = NeutralIpcConfig.get_buffer_size()

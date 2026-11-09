"""
Configuration management for Note Type Export add-on.
"""

from typing import Any


class ConfigKey:
    """Configuration keys for the add-on."""
    # What to do when importing a note type with a name that already exists
    # Options: "ask", "rename", "overwrite", "skip"
    DEFAULT_CONFLICT_ACTION = 'default_conflict_action'
    
    # Whether to include metadata (export date, anki version) in exports
    EXPORT_INCLUDE_METADATA = 'export_include_metadata'
    
    # Last used directories for file dialogs
    LAST_EXPORT_DIR = 'last_export_dir'
    LAST_IMPORT_DIR = 'last_import_dir'


class ConflictAction:
    """Possible actions when a name conflict occurs during import."""
    ASK = 'ask'           # Ask the user each time
    RENAME = 'rename'     # Auto-rename with "(imported)" suffix
    OVERWRITE = 'overwrite'  # Overwrite existing note type
    SKIP = 'skip'         # Skip importing conflicting note types


DEFAULT_CONFIG = {
    ConfigKey.DEFAULT_CONFLICT_ACTION: ConflictAction.ASK,
    ConfigKey.EXPORT_INCLUDE_METADATA: True,
    ConfigKey.LAST_EXPORT_DIR: '',
    ConfigKey.LAST_IMPORT_DIR: '',
}


class ConfigService:
    """Service for reading and writing configuration."""
    
    # Will be replaced with Anki's config reader in binding.py
    _config_reader = None
    _config_writer = None
    
    @classmethod
    def read(cls, key: str, expected_type: type = None) -> Any:
        """Read a configuration value."""
        if cls._config_reader:
            value = cls._config_reader(key)
            if value is not None:
                if expected_type and not isinstance(value, expected_type):
                    return DEFAULT_CONFIG.get(key)
                return value
        return DEFAULT_CONFIG.get(key)
    
    @classmethod
    def write(cls, key: str, value: Any) -> None:
        """Write a configuration value."""
        if cls._config_writer:
            cls._config_writer(key, value)
    
    @classmethod
    def set_config_reader(cls, reader) -> None:
        """Set the config reader function."""
        cls._config_reader = reader
    
    @classmethod
    def set_config_writer(cls, writer) -> None:
        """Set the config writer function."""
        cls._config_writer = writer

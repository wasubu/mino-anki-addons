"""
Anki integration for Note Type Export add-on.
Sets up menu items and connects to Anki's APIs.
"""

from aqt import mw
from aqt.qt import QAction, qconnect
from aqt.utils import showInfo, showWarning, tooltip

from .config import ConfigService


def _anki_config_read(key: str):
    """Read config value from Anki's addon manager."""
    config = mw.addonManager.getConfig(__name__.split('.')[0])
    if config:
        return config.get(key)
    return None


def _anki_config_write(key: str, value):
    """Write config value to Anki's addon manager."""
    config = mw.addonManager.getConfig(__name__.split('.')[0]) or {}
    config[key] = value
    mw.addonManager.writeConfig(__name__.split('.')[0], config)


def on_export_note_types():
    """Handle export menu action."""
    if not mw.col:
        showWarning("Please open a profile first.")
        return
    
    from .dialogs import ExportDialog
    dialog = ExportDialog(mw)
    dialog.exec()


def on_import_note_types():
    """Handle import menu action."""
    if not mw.col:
        showWarning("Please open a profile first.")
        return
    
    from .importer import import_note_types_from_file
    import_note_types_from_file(mw)


def _setup_menus():
    """Add menu items to Anki's Tools menu."""
    # Export action
    export_action = QAction("Export Note Types...", mw)
    export_action.setStatusTip("Export note types to a JSON file")
    qconnect(export_action.triggered, on_export_note_types)
    mw.form.menuTools.addAction(export_action)
    
    # Import action
    import_action = QAction("Import Note Types...", mw)
    import_action.setStatusTip("Import note types from a JSON file")
    qconnect(import_action.triggered, on_import_note_types)
    mw.form.menuTools.addAction(import_action)


def run():
    """Initialize the add-on."""
    # Set up config service
    ConfigService.set_config_reader(_anki_config_read)
    ConfigService.set_config_writer(_anki_config_write)
    
    # Set up menus
    _setup_menus()

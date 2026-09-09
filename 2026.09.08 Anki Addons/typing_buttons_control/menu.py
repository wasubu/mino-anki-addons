from aqt import gui_hooks, mw
from aqt.qt import QAction, QMenu
from aqt.utils import tooltip

ADDON_PACKAGE = __name__.split(".")[0]


def get_config() -> dict:
    """Reads current configuration or returns defaults if missing."""
    return mw.addonManager.getConfig(ADDON_PACKAGE) or {
        "enable_only_again": True,
        "enable_multi_typebox": True,
    }


def _toggle_feature(config_key: str, action: QAction, feature_name: str):
    """Updates config on disk and informs user to restart Anki."""
    config = get_config()
    is_checked = action.isChecked()
    config[config_key] = is_checked
    mw.addonManager.writeConfig(ADDON_PACKAGE, config)

    status = "enabled" if is_checked else "disabled"
    tooltip(f"[{feature_name}] {status}. Restart Anki to apply changes.")


def setup_menu():
    """Builds the Tools menu entry with checkable options."""
    addon_menu = QMenu("Typing & Buttons Control", mw)
    mw.form.menuTools.addAction(addon_menu.menuAction())

    config = get_config()

    # Toggle 1: ONLY_AGAIN Tag Logic
    action_only_again = QAction("Enable ONLY_AGAIN Tag Logic", addon_menu)
    action_only_again.setCheckable(True)
    action_only_again.setChecked(config.get("enable_only_again", True))
    action_only_again.triggered.connect(
        lambda: _toggle_feature("enable_only_again", action_only_again, "ONLY_AGAIN Logic")
    )
    addon_menu.addAction(action_only_again)

    # Toggle 2: Multi-Line Typebox
    action_multi_typebox = QAction("Enable Multi-Line Typebox", addon_menu)
    action_multi_typebox.setCheckable(True)
    action_multi_typebox.setChecked(config.get("enable_multi_typebox", True))
    action_multi_typebox.triggered.connect(
        lambda: _toggle_feature("enable_multi_typebox", action_multi_typebox, "Multi-Line Typebox")
    )
    addon_menu.addAction(action_multi_typebox)


def setup():
    """Initializes menu construction once Anki main window loads."""
    gui_hooks.main_window_did_init.append(setup_menu)
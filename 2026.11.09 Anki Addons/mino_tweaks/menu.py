from pathlib import Path
import pkgutil
from aqt import mw
from aqt.qt import QAction, QMenu

MENU_TITLE = "Mino"


def _get_or_create_mino_menu() -> QMenu:
    """Find existing 'Mino' menu in main menubar or create a new one."""
    menubar = mw.form.menubar
    for action in menubar.actions():
        if action.text() == MENU_TITLE:
            return action.menu()
    return menubar.addMenu(MENU_TITLE)


def setup_addon_menu():
    mino_menu = _get_or_create_mino_menu()

    config = mw.addonManager.getConfig(__name__) or {}
    disabled_tweaks = set(config.get("disabled_tweaks", []))

    tweaks_dir = Path(__file__).parent / "tweaks"
    if not tweaks_dir.is_dir():
        return

    # Populate root Mino menu directly with tweak toggles
    for _, module_name, is_pkg in pkgutil.iter_modules([str(tweaks_dir)]):
        if is_pkg or module_name.startswith("_"):
            continue

        display_name = module_name.replace("_", " ").title()
        action = QAction(display_name, mino_menu)
        action.setCheckable(True)
        action.setChecked(module_name not in disabled_tweaks)

        # Scoped toggle callback to write config on click
        def _make_handler(name):
            def _toggle(checked: bool):
                cfg = mw.addonManager.getConfig(__name__) or {}
                disabled = set(cfg.get("disabled_tweaks", []))
                if checked:
                    disabled.discard(name)
                else:
                    disabled.add(name)
                cfg["disabled_tweaks"] = list(disabled)
                mw.addonManager.writeConfig(__name__, cfg)

            return _toggle

        action.triggered.connect(_make_handler(module_name))
        mino_menu.addAction(action)
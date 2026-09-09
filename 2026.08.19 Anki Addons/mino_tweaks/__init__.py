import importlib
import pkgutil
import traceback
from pathlib import Path
from aqt import mw

from .menu import setup_addon_menu


def _load_enabled_tweaks():
    config = mw.addonManager.getConfig(__name__) or {}
    disabled_tweaks = set(config.get("disabled_tweaks", []))

    tweaks_dir = Path(__file__).parent / "tweaks"
    if not tweaks_dir.is_dir():
        return

    for _, module_name, is_pkg in pkgutil.iter_modules([str(tweaks_dir)]):
        if is_pkg or module_name.startswith("_") or module_name in disabled_tweaks:
            continue

        try:
            mod = importlib.import_module(f".tweaks.{module_name}", package=__name__)
            if hasattr(mod, "setup") and callable(mod.setup):
                mod.setup()
        except Exception as e:
            print(f"[Tweaks Addon] Failed to load tweak '{module_name}': {e}")
            traceback.print_exc()


# Initialize UI menu and load tweaks on startup
setup_addon_menu()
_load_enabled_tweaks()
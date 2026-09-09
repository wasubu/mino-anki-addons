import importlib
import pkgutil
import traceback
from pathlib import Path


def _load_all_tweaks():
    tweaks_dir = Path(__file__).parent / "tweaks"
    if not tweaks_dir.is_dir():
        return

    for _, module_name, is_pkg in pkgutil.iter_modules([str(tweaks_dir)]):
        if is_pkg or module_name.startswith("_"):
            continue

        try:
            mod = importlib.import_module(f".tweaks.{module_name}", package=__name__)
            if hasattr(mod, "setup") and callable(mod.setup):
                mod.setup()
        except Exception as e:
            print(f"[Tweaks Addon] Failed to load tweak '{module_name}': {e}")
            traceback.print_exc()


_load_all_tweaks()
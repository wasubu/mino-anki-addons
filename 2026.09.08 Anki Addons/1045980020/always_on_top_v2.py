# AlwaysOnTop
# Copyright (C) Damien Elmes ? <anki@ichi2.net>
# Copyright (C) Glutanimate ? <github.com/glutanimate>
# Copyright (C) Unknow 2019 <https://ankiweb.net/shared/info/1760080335>
# Copyright (C) Shigeyuki 2025 <http://patreon.com/Shigeyuki>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from aqt import mw, gui_hooks

try:
    from PyQt6.QtWidgets import QWidget, QMenu, QFileDialog
    from PyQt6.QtCore import Qt, QObject, QEvent, QTimer
    from PyQt6.QtGui import QAction, QKeySequence
except Exception as e:
    print(f"[AlwaysOnTop] Error: {e} ")
    from aqt.qt import QWidget, QMenu, QFileDialog
    from aqt.qt import Qt, QObject, QEvent, QTimer
    from aqt.qt import QAction, QKeySequence

from .path_manager import HUMAN_ADDON_NAME, ADDON_NAME

is_reversal = True
mw._onTop = False
is_always_on_top = None
is_first_run = True


# for exists windows
#MARK:alwaysOnTop
def alwaysOnTop():
    global is_reversal, is_always_on_top
    config = mw.addonManager.getConfig(__name__)
    if is_reversal:
        config["is_always_on_top"] = mw._onTop = not mw._onTop
        mw.addonManager.writeConfig(__name__, config)
    else:
        is_reversal = True
    is_always_on_top.setChecked(mw._onTop)

    windows: list[QWidget] = []

    for instance in mw.app.topLevelWidgets():
        if isinstance(instance, QWidget) and instance.isWindow():
            windows.append(instance)

    for window in windows:

        if isinstance(window, QFileDialog):
            continue

        if window.isVisible() and not window.isMinimized():
            if mw._onTop:
                window.setWindowFlags(window.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            else:
                window.setWindowFlags(window.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            window.show()

            # print(f"[AlwaysOnTop] show: {window.objectName()} {window.windowTitle()}")

    if config.get("activate_window", True):
        mw.raise_()
        mw.activateWindow()

    if not is_first_run:
        try:
            from aqt.utils import tooltip
            if mw._onTop:
                tooltip("[🔝Always on top ] Enabled! :-)")
            else:
                tooltip("[🔝Always on top ] Disabled :-/")

        except Exception as e:
            print(f"[{ADDON_NAME}] Error: {e}")
            pass

#MARK:setup_addon_menu
def setup_addon_menu(*args, **kwargs):
    global is_always_on_top

    addon_menu = QMenu(HUMAN_ADDON_NAME, mw)
    mw.form.menuTools.addAction(addon_menu.menuAction())

    is_always_on_top = QAction("Enable Always on top", addon_menu)
    is_always_on_top.setCheckable(True)

    try:
        config = mw.addonManager.getConfig(__name__)
        shortcut_key = config.get("shortcut_key", "Alt+A")
        is_always_on_top.setShortcut(QKeySequence(shortcut_key))
    except Exception as e:
        print(f"[{ADDON_NAME}] Error: {e}")

    is_always_on_top.triggered.connect(alwaysOnTop)

    addon_menu.addAction(is_always_on_top)

    addon_menu.addSeparator()

    from .shige_config.addon_config import set_config_and_menu
    set_config_and_menu(addon_menu)

    addon_menu.addSeparator()

    rate_this_action = QAction('👍️RateThis', mw)
    rate_this_action.triggered.connect(lambda: open_popup_url("rate"))
    addon_menu.addAction(rate_this_action)

    patreon_action = QAction("💖Become a Patron", mw)
    patreon_action.triggered.connect(lambda: open_popup_url("patreon"))
    addon_menu.addAction(patreon_action)


#MARK:open url
def open_popup_url(key):
    try:
        from .shige_config.popup_config import REPORT_URL, PATREON_URL, RATE_THIS_URL
        from aqt.utils import openLink
        url_map = {
            "rate": RATE_THIS_URL,
            "patreon": PATREON_URL,
            "report": REPORT_URL,
        }
        openLink(url_map[key])

    except Exception as e:
        print(f"[{ADDON_NAME}] Error: {e}")


#MARK: shortcut key
#📍use from config
def update_shortcut_key_config():
    try:
        global is_always_on_top
        if isinstance(is_always_on_top, QAction):
            config = mw.addonManager.getConfig(__name__)
            shortcut_key = config.get("shortcut_key", "Alt+A")
            is_always_on_top.setShortcut(QKeySequence(shortcut_key))

    except Exception as e:
        print(f"[{ADDON_NAME}] Error: {e}")


#MARK: setup
def alwaysOnTop_setup(*args,**kwargs):
    global is_reversal, is_always_on_top, is_first_run

    setup_addon_menu()

    config = mw.addonManager.getConfig(__name__)
    mw._onTop = config.get("is_always_on_top", True)
    is_always_on_top.setChecked(mw._onTop)
    if mw._onTop:
        is_reversal = False
        alwaysOnTop()

    is_first_run = False


# for all new windows
#MARK:AlwaysOnTopFilter
class AlwaysOnTopFilter(QObject):
    def eventFilter(self, obj: QObject, event: QEvent):
        if event.type() == QEvent.Type.Show and isinstance(obj, QWidget) and obj.isWindow():
            try:
                if mw._onTop:

                    if isinstance(obj, QFileDialog):
                        return False

                    if not (obj.windowFlags() & Qt.WindowType.WindowStaysOnTopHint):

                        obj.setWindowFlags(obj.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

                        def restore():
                            try:
                                if obj.isFullScreen():
                                    obj.showFullScreen()
                                elif obj.isMaximized():
                                    obj.showMaximized()
                                else:
                                    obj.show()
                            except RuntimeError:
                                pass

                        QTimer.singleShot(0, restore)

            except Exception as e:
                print(f"[{ADDON_NAME}] Error: {e}")
                pass
        return False

#MARK:hooks
def set_hooks():
    always_on_top_filter = AlwaysOnTopFilter(mw.app)
    mw.app.installEventFilter(always_on_top_filter)
    gui_hooks.main_window_did_init.append(alwaysOnTop_setup)


#MARK:wrap

# for showMaximized support (win11)
from aqt.qt import QMainWindow

_original_QMainwindow_init = QMainWindow.__init__

def wrapped_QMainwindow_init(self, parent=None, flags=Qt.WindowType.Window):
    if getattr(mw, "_onTop", False):
        flags = flags | Qt.WindowType.WindowStaysOnTopHint

    _original_QMainwindow_init(self, parent, flags)

QMainWindow.__init__ = wrapped_QMainwindow_init
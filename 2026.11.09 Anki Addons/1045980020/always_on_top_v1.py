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

from anki.hooks import wrap

from aqt import dialogs,gui_hooks
from aqt import mw, addcards, editcurrent, browser
from aqt.qt import *

is_reversal = True

def alwaysOnTop():
    global is_reversal
    config = mw.addonManager.getConfig(__name__)

    if is_reversal:
        config["is_always_on_top"] = mw._onTop = not mw._onTop
        mw.addonManager.writeConfig(__name__,config)
    else:
        is_reversal = True

    action.setChecked(mw._onTop)

    windows = [mw]
    for dclass, instance in dialogs._dialogs.values():
        if instance:
            windows.append(instance)
    for window in windows:
        windowFlags = window.windowFlags()
        windowFlags ^= Qt.WindowType.WindowStaysOnTopHint
        window.setWindowFlags(windowFlags)
        window.show()

def onWindowInit(self, *args, **kwargs):
    if mw._onTop:
        windowFlags = self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        self.show()

# mw._onTop = False

action = QAction("Always On Top V1 (Fixed by Shigeඞ)", mw)
action.setCheckable(True)
mw._onTop = False
action.triggered.connect(alwaysOnTop)
mw.form.menuTools.addAction(action)

def alwaysOnTop_setup(*args,**kwargs):
    global is_reversal
    config = mw.addonManager.getConfig(__name__)
    mw._onTop = config["is_always_on_top"]
    action.setChecked(mw._onTop)
    if mw._onTop:
        is_reversal = False
        alwaysOnTop()

gui_hooks.main_window_did_init.append(alwaysOnTop_setup)

addcards.AddCards.__init__ = wrap(addcards.AddCards.__init__, onWindowInit, "after")
editcurrent.EditCurrent.__init__ = wrap(editcurrent.EditCurrent.__init__, onWindowInit, "after")
browser.Browser.__init__ = wrap(browser.Browser.__init__, onWindowInit, "after")

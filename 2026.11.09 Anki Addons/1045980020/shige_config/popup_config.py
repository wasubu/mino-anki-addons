# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

import os
import random

try:
    from PyQt6.QtWidgets import (
        QDialog, QHBoxLayout, QTabWidget, QWidget, QSizePolicy,
        QVBoxLayout, QLabel, QPushButton
    )
    from PyQt6.QtGui import QIcon, QResizeEvent, QPixmap
    from PyQt6.QtCore import QUrl, Qt
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings

except Exception as e:
    print(f"PyQt6 Import Error: {e} ")
    from aqt.qt import (
        QDialog, QHBoxLayout, QTabWidget, QWidget, QSizePolicy,
        QVBoxLayout, QLabel, QPushButton
    )
    from aqt.qt import QIcon, QResizeEvent, QPixmap
    from aqt.qt import QUrl, Qt
    from aqt.qt import QWebEngineView
    from aqt.qt import QWebEnginePage, QWebEngineSettings

from .button_manager import mini_button
from .shige_addons import add_shige_addons_tab
from .endroll.endroll import add_credit_tab

from .change_log import OLD_CHANGE_LOG
from .patrons_list import PATRONS_LIST

from ..path_manager import HUMAN_ADDON_NAME, ADDON_NAME

CHANGE_LOG = "is_change_log"
CHANGE_LOG_DAY = "2025-10-24d" #🟢


ICON_PATH = r"popup_icon.png"


REPORT_URL = "https://shigeyukey.github.io/shige-addons-wiki/contact.html"


# popup-size
# mini-pupup
SIZE_MINI_WIDTH = 764
SIZE_MINI_HEIGHT = 480
# Width: 764, Height: 480

ANKI_WEB_URL = ""
RATE_THIS_URL = ""

from aqt import mw
ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
# ｱﾄﾞｵﾝのURLが数値であるか確認
if (isinstance(ADDON_PACKAGE, (int, float))
    or (isinstance(ADDON_PACKAGE, str)
    and ADDON_PACKAGE.isdigit())):
    ANKI_WEB_URL = f"https://ankiweb.net/shared/info/{ADDON_PACKAGE}"
    RATE_THIS_URL = f"https://ankiweb.net/shared/review/{ADDON_PACKAGE}"


PATREON_URL = "http://patreon.com/Shigeyuki"
REDDIT_URL = "https://www.reddit.com/r/Anki/comments/1b0eybn/simple_fix_of_broken_addons_for_the_latest_anki/"

POPUP_PNG = r"popup_shige.png"


#🟢
NEW_FEATURE = """
2025-10-24
[1] Enhanced: Always on top V2
- Added support for all windows. (Card Info, Add-ons, etc.)
- Added a shortcut key. (default: Alt+A)
- Added tooltip feedback.
- Added option Window, optimized some code.
2025-10-27: Added support Maximized.
2025-11-27: Fixed a small bug.

Note:
- If you want to restore to V1 or encounter problems you can restore to the older version by setting enable_v2 to false in config. (need to restart Anki)
"""


UPDATE_TEXT = "I updated this Add-on."

SPECIAL_THANKS ="""\
[ Patreon ] Special thanks
Without the support of my Patrons, I would never have been
able to develop this. Thank you very much!🙏"""



#🟢
#MARK:add-ons status
INT_FIXED = 80 # fixed addons
INT_ORIGIN = 30 # origin free addons
INT_DONATE = 5 # donation
INT_PATREON_ADDONS = 17 # patron add-ons



#MARK:make PR
# -- PR patreon start ----

LIST_PATREON_ADDONS = [
                        "ankiarcade", "leaderboardPlus", "newCardFarm",
                        "chunkProgressBar"
                        ]

# STR_PR_PT_ADDON_NAME = "ankiarcade"
# STR_PR_PT_ADDON_NAME = "leaderboardPlus"
# STR_PR_PT_ADDON_NAME = "newCardFarm"
STR_PR_PT_ADDON_NAME  = random.choice(LIST_PATREON_ADDONS)
# print(f"[{ADDON_NAME}] choice: {STR_PR_PT_ADDON_NAME} ")


THUMBNAIL_ANKI_ARCADE = "thumbnail_ankiarcade.webp"
THUMBNAIL_LEADERBOARD_PLUS = "thumbnail_Leaderboard_plus.webp"
THUMBNAIL_NEW_CARD_FARM = "thumbnail_new_card_farm.webp"
THUMBNAIL_CHUNK_PROGRESSBAR = "thumbnail_chunk_progressbar.webp"


URL_PATREON = "https://www.patreon.com/Shigeyuki/"

#📍patreon urls
URL_ANKI_ARCADE = "https://www.patreon.com/posts/136548011"
URL_LEADERBOARD_PLUS = "https://www.patreon.com/posts/154968535"
URL_NEW_CARD_FARM = "https://www.patreon.com/posts/109314080"
URL_CHUNK_PROGRESSBAR = "https://www.patreon.com/posts/101345722"



def make_patron_pr_text():

    #MARK: anki arcade
    if STR_PR_PT_ADDON_NAME == "ankiarcade":
        str_sumbnail_name = THUMBNAIL_ANKI_ARCADE
        str_patreon_url = URL_ANKI_ARCADE
        str_patron_url_href = f'<a href="{str_patreon_url}" target="_blank">'
        str_addon_distraction = f"""\
[ {str_patron_url_href}AnkiArcade (Patrons only)</a> ] AnkiArcade is a multi minigame Anki add-on that I am primarily developing. Aiming for quality comparable to indie games, it currently features 40+ animated pixel art characters, 400+ sound effects, 500+ BGM tracks, and 400+ pixel art enemy characters, progress bar, pomodoro timer, and more! If you become a Patron you can use it. (Not related to the official Anki.)"""

    #MARK: leaderboard plus
    elif STR_PR_PT_ADDON_NAME == "leaderboardPlus":
        str_sumbnail_name = THUMBNAIL_LEADERBOARD_PLUS
        str_patreon_url = URL_LEADERBOARD_PLUS
        str_patron_url_href = f'<a href="{str_patreon_url}" target="_blank">'
        str_addon_distraction = f"""\
[ {str_patron_url_href}🏆️Anki Leaderboard Plus (Patrons only)</a> ] Leaderboard displayed on top bar and updated in real time during review! This version added sync speed optimization and enhancements, UI for gamification mode, toast notifications for scores, improved tooltip design, and enhanced options, etc. Revenue from this add-on will be used to maintain and enhance the leaderboard Free server. (Not related to the official Anki.)"""

    #MARK: new card farm
    elif STR_PR_PT_ADDON_NAME == "newCardFarm":
        str_sumbnail_name = THUMBNAIL_NEW_CARD_FARM
        str_patreon_url = URL_NEW_CARD_FARM
        str_patron_url_href = f'<a href="{str_patreon_url}" target="_blank">'
        str_addon_distraction = f"""\
[ {str_patron_url_href}🌱New Cards Farm 2 (Patrons only)</a> ] You can grow crops and flowers with the new cards you have learned. Crops 79, Color tooltip, Farmer animation, Random Crops, Replanting Crops, etc. (Not related to the official Anki.)"""


    #MARK: chunk progressbar
    elif STR_PR_PT_ADDON_NAME == "chunkProgressBar":
        str_sumbnail_name = THUMBNAIL_CHUNK_PROGRESSBAR
        str_patreon_url = URL_CHUNK_PROGRESSBAR
        str_patron_url_href = f'<a href="{str_patreon_url}" target="_blank">'
        str_addon_distraction = f"""\
[ {str_patron_url_href}⌛️Chunk Progressbar (Patrons only)</a> ] This add-on is an enhanced version of Progress bar for chunking Anki cards, add two progress bars to the top of Anki. Revenue from this add-on will be used to maintain and enhance the Free Progressbar add-on. (Not related to the official Anki.)"""

    try:
        _patreon_addon_path = os.path.join(os.path.dirname(__file__), str_sumbnail_name)
        str_patreon_addon_path = (
            f'{str_patron_url_href}'
            f'<img src="{_patreon_addon_path}"></a>'
        )
    except Exception as e:
        print(f"Error: {e} ")
        str_patreon_addon_path = ""

    str_patreon_pr_text = f"""\
{str_patreon_addon_path}
{str_addon_distraction}"""

    return str_patreon_pr_text

try:
    str_patreon_pr_text = make_patron_pr_text()
except Exception as e:
    print(f"[{ADDON_NAME}] Error: {e}")
    str_patreon_pr_text = ""


STR_PATREN_PR_TEXT = f"""\
[ 🎮Shige's Gamification add-ons ] I develop as a hobby and so far I've fixed {INT_FIXED}+ broken add-ons for free by request from users and released {INT_ORIGIN}+ original add-ons for free! If you become a patron (${INT_DONATE}/month) and support my volunteer development you can get exclusive gamification add-ons {INT_PATREON_ADDONS}+ for Patrons.
{str_patreon_pr_text}"""


# --- PR patreon end ---




CHANGE_LOG_TEXT = f"""\
[ Change log : {HUMAN_ADDON_NAME} ]

Shigeyuki : Hi thanks for using this add-on! {UPDATE_TEXT}
{NEW_FEATURE}
--------
{STR_PATREN_PR_TEXT}
--------

[ Old change log ]
{OLD_CHANGE_LOG}

{SPECIAL_THANKS}

{PATRONS_LIST}
"""


#MARK:set hooks
def set_gui_hook_change_log():
    from aqt import gui_hooks
    gui_hooks.main_window_did_init.append(change_log_popup)
    # gui_hooks.main_window_did_init.append(add_config_button)

def change_log_popup(*args,**kwargs):
    try:
        from aqt import mw
        config = mw.addonManager.getConfig(__name__)
        if (config.get(CHANGE_LOG) != CHANGE_LOG_DAY):
            dialog = CustomDialog(mw, CHANGE_LOG_TEXT)
            dialog.show()
            config[CHANGE_LOG] =  CHANGE_LOG_DAY
            mw.addonManager.writeConfig(__name__, config)

    except Exception as e:
        print(f"[{ADDON_NAME}] Error: {e} ")


#MARK:open link
def on_open_link(url):
    from aqt.utils import openLink
    openLink(url)


#MARK:EnginePage
# gifｱﾆﾒを表示するためにQWebEngineを使う
class CustomWebEnginePage(QWebEnginePage):

    def createWindow(self, _type):
        new_page = CustomWebEnginePage(self)
        new_page.urlChanged.connect(on_open_link)
        return new_page

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        pass


#MARK:make html
def make_change_log_html(change_log_text:str):

    escaped_text = change_log_text.replace("\n", "<br>")

    is_dark_mode = True
    try:
        from aqt.theme import theme_manager
        is_dark_mode = theme_manager.night_mode
    except Exception as e:
        print(f"[{ADDON_NAME}] Error: {e}")
        is_dark_mode = True

    if is_dark_mode:
        bg_color = "#2b2b2b"
        text_color = "#e0e0e0"
        link_color = "#64b5f6"
        visited_color = "#ba68c8"
        scrollbar_thumb = "rgba(120, 120, 120, 0.7)"
        scrollbar_track = "#1e1e1e"
    else:
        bg_color = "#ffffff"
        text_color = "#000000"
        link_color = "#0066cc"
        visited_color = "#7030a0"
        scrollbar_thumb = "rgba(150, 150, 150, 0.7)"
        scrollbar_track = "#f5f5f5"

    str_html =  f"""
<html>
<head>

<style>
body {{
    font-family: system-ui;
    font-size: 12px;
    background-color: {bg_color};
    color: {text_color};
    margin: 0;
    padding: 10px;
}}

a {{
    color: {link_color};
}}

a:visited {{
    color: {visited_color};
}}

a:hover {{
    text-decoration: underline;
}}

::-webkit-scrollbar {{
    width: 12px;
}}
::-webkit-scrollbar-track {{
    background: {scrollbar_track};
}}
::-webkit-scrollbar-thumb {{
    background-color: {scrollbar_thumb};
    border-radius: 6px;
    border: 2px solid transparent;
    background-clip: content-box;
}}
::-webkit-scrollbar-thumb:hover {{
    background-color: rgba(180, 180, 180, 0.9);
}}

</style>
    </head>
    <body>
        <div style="white-space: pre-wrap;">{escaped_text}</div>
    </body>
</html>
"""
    return str_html


#MARK:CustomDialog
class CustomDialog(QDialog):

    def __init__(self, parent=None, change_log_text=CHANGE_LOG_TEXT):
        super().__init__(parent)

        try:
            addon_path = os.path.dirname(__file__)
            icon = QPixmap(os.path.join(addon_path, POPUP_PNG))

            self.resize(SIZE_MINI_WIDTH, SIZE_MINI_HEIGHT)

            qt_icon_for_dialog = QIcon(os.path.join(addon_path, ICON_PATH))
            self.setWindowIcon(qt_icon_for_dialog)

            self.setWindowTitle(HUMAN_ADDON_NAME)

            qt_tab_widget = QTabWidget()
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)

            icon_label = QLabel()
            icon_label.setPixmap(icon)

            hbox_layout = QHBoxLayout()

            change_log_label = QWebEngineView(tab)
            change_log_label.setPage(CustomWebEnginePage(change_log_label))
            change_log_label.settings().setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
            )
            change_log_label.settings().setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
            )
            change_log_label.settings().setAttribute(
                QWebEngineSettings.WebAttribute.JavascriptEnabled, True
            )
            change_log_label.setHtml(
                make_change_log_html(change_log_text),
                baseUrl=QUrl.fromLocalFile(addon_path + "/"),
            )
            change_log_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


            hbox_layout.addWidget(icon_label)
            hbox_layout.addWidget(change_log_label)

            tab_layout.addLayout(hbox_layout)

            button_layout = QHBoxLayout()
            button_layout.addStretch()

            self.yes_button = QPushButton("💖Become a Patron")
            self.yes_button.clicked.connect(lambda: on_open_link(PATREON_URL))
            self.yes_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            mini_button(self.yes_button)

            self.report_button = QPushButton("🚨Report")
            self.report_button.clicked.connect(lambda: on_open_link(REPORT_URL))
            self.report_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            mini_button(self.report_button)

            self.no_button = QPushButton("OK (Close)")
            self.no_button.clicked.connect(self.close)
            self.no_button.setFixedWidth(120)

            button_layout.addWidget(self.yes_button)
            button_layout.addWidget(self.report_button)
            button_layout.addWidget(self.no_button)

            qt_tab_widget.addTab(tab, "Change Log")
            add_credit_tab(self, qt_tab_widget)
            add_shige_addons_tab(self, qt_tab_widget)

            main_layout = QVBoxLayout(self)
            main_layout.addWidget(qt_tab_widget)
            main_layout.addLayout(button_layout)

            self.setLayout(main_layout)

        except Exception as e:
            print(f"[{ADDON_NAME}] Erorr: {e} ")


    #MARK:resizeEvent
    def resizeEvent(self, event:"QResizeEvent"):
        size = event.size()
        print(f"Width: {size.width()}, Height: {size.height()}")
        super().resizeEvent(event)


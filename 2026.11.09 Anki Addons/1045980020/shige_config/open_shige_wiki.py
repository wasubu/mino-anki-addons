# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

from aqt import QLabel, Qt
from aqt.utils import openLink
import urllib.parse

try:
    from aqt.theme import theme_manager
except ImportError:
    theme_manager = None

ICON_SIZE = 16

def get_svg_question_mark():
    if theme_manager and theme_manager.night_mode:
        fill_color = "#DADADA"
    else:
        fill_color = "#5C5F62"

    svg_data = f"""<svg width="16" height="16" viewBox="0 0 0.32 0.32" xmlns="http://www.w3.org/2000/svg"><path  d="M.16 0C.072 0 0 .072 0 .16s.072.16.16.16S.32.248.32.16.248 0 .16 0m.018.261h-.04v-.04h.04zM.221.162.197.176C.184.184.181.181.181.2h-.04c0-.04.024-.053.04-.061L.194.131Q.2.129.197.118A.034.034 0 0 0 .163.097c-.029 0-.032.024-.034.03L.088.121A.07.07 0 0 1 .16.058c.032 0 .061.018.072.045q.013.034-.013.06"
    fill="{fill_color}"/>
    </svg>"""

    return svg_data

class WikiQLabel(QLabel):
    """
        new_label = WikiQLabel( "<b>[ Shige Wiki]</b>",
            "https://shigeyukey.github.io/shige-addons-wiki/")
"""

    def __init__(self, text, url=None, parent=None):
        super().__init__(parent)

        if isinstance(text, QLabel):
            original_text = text.text()
            text.deleteLater()
            text = original_text

        self.url = url
        self.update_text(text, url)

        self.setOpenExternalLinks(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.linkActivated.connect(self.open_link)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def open_link(self, link):
        openLink(link)

    def update_text(self, text, url=None):
        if url is not None:
            self.url = url

        if self.url == "":
            new_text = f"{text}"
        else:
            svg = get_svg_question_mark()
            data_uri = "data:image/svg+xml;charset=utf-8," + urllib.parse.quote(svg)
            new_text = f'{text} <a href="{self.url}" style="text-decoration:none; vertical-align: middle;"><img src="{data_uri}" width="{ICON_SIZE}" height="{ICON_SIZE}" /></a>'
        self.setText(new_text)

    def updateTextAndUrl(self, text, url):
        self.update_text(text, url)

# e.g.
# new_label = WikiQLabel(
#     "<b>[ Shige Wiki]</b>",
#     "https://shigeyukey.github.io/shige-addons-wiki/")
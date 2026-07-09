
from aqt.qt import QTextBrowser, QVBoxLayout


def add_change_log_layout(layout:QVBoxLayout):
    try:
        shortcuts_tb = QTextBrowser()
        from .popup_config import NEW_FEATURE
        from .change_log import OLD_CHANGE_LOG
        change_log_text = f"[ Change log ]<br>{NEW_FEATURE}<br>{OLD_CHANGE_LOG}"
        change_log_text = change_log_text.replace("\n", "<br>")
        shortcuts_tb.setHtml(change_log_text)
        layout.addWidget(shortcuts_tb)
    except Exception as e:
        print(f"[ZoomAnki] Error: {e}")

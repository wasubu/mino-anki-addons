from aqt import gui_hooks
from aqt.reviewer import Reviewer

_orig_defaultEase = None
_orig_answerCard = None


def _has_target_tag(card) -> bool:
    if not card or not card.note():
        return False
    return card.note().has_tag("ONLY_AGAIN")


def _force_only_again_button(buttons_tuple, reviewer, card):
    if _has_target_tag(card):
        return ((1, "Again"),)
    return buttons_tuple


def _patched_defaultEase(self):
    # Disable Spacebar/Enter answering action for ONLY_AGAIN cards
    if self.card and _has_target_tag(self.card):
        return None
    return _orig_defaultEase(self)


def _patched_answerCard(self, ease):
    # Ignore answer trigger if defaultEase returned None
    if ease is None:
        return
    return _orig_answerCard(self, ease)


def _disable_space_in_webview(reviewer):
    card = getattr(reviewer, "card", None)
    if _has_target_tag(card):
        reviewer.web.eval("""
            document.onkeydown = function(e) {
                if (e.key === " " || e.key === "Enter") {
                    e.preventDefault();
                    e.stopPropagation();
                }
            };
        """)


def setup():
    global _orig_defaultEase, _orig_answerCard

    # 1. Restrict buttons on screen to "Again" only
    gui_hooks.reviewer_will_init_answer_buttons.append(_force_only_again_button)

    # 2. Block webview keypress events on answer screen
    gui_hooks.reviewer_did_show_answer.append(_disable_space_in_webview)

    # 3. Patch defaultEase so Spacebar/Enter do nothing on answer screen
    if _orig_defaultEase is None:
        _orig_defaultEase = Reviewer._defaultEase
        Reviewer._defaultEase = _patched_defaultEase

    if _orig_answerCard is None:
        _orig_answerCard = Reviewer._answerCard
        Reviewer._answerCard = _patched_answerCard
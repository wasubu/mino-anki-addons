from aqt import gui_hooks, mw
from aqt.reviewer import Reviewer

_orig_defaultEase = None


def _has_target_tag(card) -> bool:
    if not card or not card.note():
        return False
    return card.note().has_tag("ONLY_AGAIN")


def _force_only_again_button(buttons_tuple, reviewer, card):
    if _has_target_tag(card):
        return ((1, "Again"),)
    return buttons_tuple


def _force_again_ease(ease_tuple, reviewer, card):
    # Allow Good to pass if we are in the bypass state
    if getattr(reviewer, "_bypassing_only_again", False):
        return ease_tuple

    if _has_target_tag(card):
        cont, _ = ease_tuple
        return (cont, 1)
    return ease_tuple


def _patched_defaultEase(self):
    # Return 1 for Spacebar/Enter so default actions pass ease=1 to _answerCard
    if self.card and _has_target_tag(self.card):
        return 1
    return _orig_defaultEase(self)


def _handle_js_message(
    handled: tuple[bool, any], message: str, context: any
) -> tuple[bool, any]:
    if message == "mino_rate_good":
        reviewer = getattr(mw, "reviewer", None)
        if reviewer and reviewer.card:
            card = reviewer.card

            button_count = mw.col.sched.answerButtons(card)
            good_ease = 2 if button_count in (2, 3) else 3

            # Set flag -> Answer card -> Clear flag
            reviewer._bypassing_only_again = True
            try:
                reviewer._answerCard(good_ease)
            finally:
                reviewer._bypassing_only_again = False

        return (True, None)

    return handled


def setup():
    """Registers hooks for ONLY_AGAIN logic and JS webview messages."""
    global _orig_defaultEase

    gui_hooks.reviewer_will_init_answer_buttons.append(_force_only_again_button)
    gui_hooks.reviewer_will_answer_card.append(_force_again_ease)
    gui_hooks.webview_did_receive_js_message.append(_handle_js_message)

    # Patch defaultEase so Spacebar triggers ease 1 natively
    if _orig_defaultEase is None:
        _orig_defaultEase = Reviewer._defaultEase
        Reviewer._defaultEase = _patched_defaultEase
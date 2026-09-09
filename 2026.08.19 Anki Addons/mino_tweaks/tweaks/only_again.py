from aqt import gui_hooks
from aqt.reviewer import Reviewer


def _has_target_tag(card) -> bool:
    if not card or not card.note():
        return False
    return card.note().has_tag("ONLY_AGAIN")


def _force_only_again_button(buttons_tuple, reviewer, card):
    if _has_target_tag(card):
        return ((1, "Again"),)
    return buttons_tuple


_orig_answerCard = Reviewer._answerCard


def _patched_answerCard(self, ease: int):
    if _has_target_tag(self.card):
        ease = 1
    return _orig_answerCard(self, ease)


def setup():
    """Registers button limits and patches answer processing."""
    gui_hooks.reviewer_will_init_answer_buttons.append(_force_only_again_button)
    Reviewer._answerCard = _patched_answerCard
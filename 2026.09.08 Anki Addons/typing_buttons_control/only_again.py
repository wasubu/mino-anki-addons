from anki.cards import Card
from aqt import gui_hooks
from aqt.reviewer import Reviewer


def _has_target_tag(card: Card) -> bool:
    if not card or not card.note():
        return False

    return card.note().has_tag("ONLY_AGAIN")


def _force_only_again_button(buttons_tuple, reviewer, card: Card):
    """Restricts the UI to show only the 'Again' button."""
    if _has_target_tag(card):
        return ((1, "Again"),)

    return buttons_tuple


# Monkey-patch _answerCard directly so third-party audio/visual add-ons
# read ease=1 BEFORE playing chimes or animations.
_old_answerCard = Reviewer._answerCard


def _only_again_safe_answerCard(self, ease):
    if self.card and _has_target_tag(self.card):
        ease = 1

    return _old_answerCard(self, ease)


def setup():
    """Registers hooks and method overrides for the ONLY_AGAIN tag logic."""
    gui_hooks.reviewer_will_init_answer_buttons.append(_force_only_again_button)
    Reviewer._answerCard = _only_again_safe_answerCard
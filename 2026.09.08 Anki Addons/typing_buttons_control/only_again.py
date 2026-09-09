from anki.cards import Card
from anki.hooks import wrap
from aqt import gui_hooks
from aqt.reviewer import Reviewer


def _force_only_again_button(buttons_tuple, reviewer, card: Card):
    """Restricts the UI to show only the 'Again' button if tagged."""
    if getattr(reviewer, "_is_only_again", False):
        return ((1, "Again"),)
    return buttons_tuple


def _only_again_answerCard(self, ease, _old):
    """Enforces ease=1 for ONLY_AGAIN cards while preserving add-on wrappers."""
    if getattr(self, "_is_only_again", False):
        ease = 1
    return _old(self, ease)


def _on_question_shown(reviewer):
    """Caches tag status ONCE per card to eliminate database lag."""
    card = reviewer.card
    reviewer._is_only_again = bool(
        card and card.note() and card.note().has_tag("ONLY_AGAIN")
    )


def setup():
    """Registers hooks and method overrides for the ONLY_AGAIN tag logic."""
    gui_hooks.reviewer_did_show_question.append(_on_question_shown)
    gui_hooks.reviewer_will_init_answer_buttons.append(_force_only_again_button)

    # wrap() preserves audio/visual chime add-ons in the execution chain
    Reviewer._answerCard = wrap(Reviewer._answerCard, _only_again_answerCard, "around")
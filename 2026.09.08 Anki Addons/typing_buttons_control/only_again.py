from aqt import gui_hooks
from anki.cards import Card


def _has_target_tag(card: Card) -> bool:
    if not card or not card.note():
        return False

    return card.note().has_tag("ONLY_AGAIN")


def _force_only_again_button(buttons_tuple, reviewer, card: Card):
    """Restricts the UI to show only the 'Again' button."""
    if _has_target_tag(card):
        return ((1, "Again"),)

    return buttons_tuple


def _force_again_ease(ease_tuple, reviewer, card: Card):
    if _has_target_tag(card):
        cont, _ = ease_tuple
        return (cont, 1)

    return ease_tuple


def setup():
    """Registers hooks for the ONLY_AGAIN tag logic."""
    gui_hooks.reviewer_will_init_answer_buttons.append(_force_only_again_button)
    gui_hooks.reviewer_will_answer_card.append(_force_again_ease)
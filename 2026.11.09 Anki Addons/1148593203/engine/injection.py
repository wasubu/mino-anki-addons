"""The reviewer injection point for aSFM.

A single ``webview_will_set_content`` handler injects one CSS file and one JS
bundle into the reviewer. Python then computes the per-card auto-reveal delay and
pushes it with a single ``ASFM.onCard(...)`` call; the JS owns the timer, the
countdown, and the warning. When the timer expires the JS asks Python to show the
answer (``asfm:reveal``). It NEVER grades the card.

The one message going the other way is ``asfm:autopause:1|0`` — the pause key
held or released the timer.
"""

import json
import os
from typing import Any, Dict, Set

from aqt import gui_hooks, mw
from aqt.reviewer import Reviewer
from aqt.sound import av_player
from aqt.utils import tooltip
from ..config import PACKAGE, get_config
from . import adaptive

PYCMD_PREFIX = "asfm:"

# The pause key's sticky state. Held here rather than in the JS so it survives
# the bundle being re-injected (leaving the reviewer and coming back), and is
# pushed out with every card payload. Cleared on profile load, not persisted.
_auto_paused = False

def auto_reveal_paused() -> bool:
    return _auto_paused


_CSS_HREF = f"/_addons/{PACKAGE}/web/asfm.css"
_JS_SRC = f"/_addons/{PACKAGE}/web/asfm.js"

# Warning alert: user_files/alert.mp3 overrides the bundled sounds/alert.mp3.
_DIR = os.path.dirname(os.path.dirname(__file__))
_DEFAULT_ALERT = os.path.join(_DIR, "sounds", "alert.mp3")
_USER_ALERT = os.path.join(_DIR, "user_files", "alert.mp3")

# FIX 1: Resolve audio path once at load/init time instead of checking disk on every cue
def _resolve_alert_path() -> str:
    return _USER_ALERT if os.path.exists(_USER_ALERT) else _DEFAULT_ALERT

_ACTIVE_ALERT = _resolve_alert_path()

def _play_alert() -> None:
    try:
        av_player.play_file(_ACTIVE_ALERT)
    except Exception:
        pass


# FIX 2: Cache config in memory to avoid repeated synchronous disk reads
_CONFIG_CACHE: Dict[str, Any] = {}
_EXCLUDED_DECK_IDS: Set[int] = set()

def _get_cfg() -> Dict[str, Any]:
    global _CONFIG_CACHE
    if not _CONFIG_CACHE:
        _CONFIG_CACHE = get_config() or {}
    return _CONFIG_CACHE

def _invalidate_config_cache(pkg: str, *args, **kwargs) -> None:
    global _CONFIG_CACHE, _EXCLUDED_DECK_IDS, _ACTIVE_ALERT
    if pkg == PACKAGE:
        _CONFIG_CACHE = get_config() or {}
        _EXCLUDED_DECK_IDS.clear()  # Force lazy re-computation of deck IDs
        _ACTIVE_ALERT = _resolve_alert_path()


# The external bundle loads async, so the first onCard() eval can arrive before it
# is ready. This inline shim buffers calls; the real bundle flushes them on load.
_SHIM = (
    "<script>(function(){if(window.ASFM)return;var q=[];var s={_queue:q};"
    "['onCard'].forEach(function(m){s[m]=function(){q.push([m,arguments]);};});"
    "window.ASFM=s;})();</script>"
)

_INJECT = (
    f'<link rel="stylesheet" href="{_CSS_HREF}">'
    f"{_SHIM}"
    f'<script src="{_JS_SRC}"></script>'
)

def _eval(js: str) -> None:
    try:
        web = mw.reviewer.web if mw.reviewer else None
        if web:
            web.eval(js)
    except Exception:
        pass


# FIX 4: Pre-compute and cache numeric deck IDs for fast set lookup O(1)
def _get_excluded_deck_ids(cfg: Dict[str, Any]) -> Set[int]:
    global _EXCLUDED_DECK_IDS
    if _EXCLUDED_DECK_IDS or not mw.col:
        return _EXCLUDED_DECK_IDS

    excluded_names = cfg.get("excluded_decks", [])
    if not excluded_names:
        return set()

    excluded_ids = set()
    all_decks = mw.col.decks.all_names_and_ids()
    for entry in excluded_names:
        if not entry:
            continue
        prefix = entry + "::"
        for deck_dict in all_decks:
            d_name = deck_dict.name
            if d_name == entry or d_name.startswith(prefix):
                excluded_ids.add(deck_dict.id)

    _EXCLUDED_DECK_IDS = excluded_ids
    return _EXCLUDED_DECK_IDS


def _excluded(card, cfg: Dict[str, Any]) -> bool:
    try:
        nt = card.note_type()
        if nt and nt.get("name") in cfg.get("excluded_note_types", []):
            return True
    except Exception:
        pass

    try:
        card_deck_id = card.current_deck_id()
        if card_deck_id in _get_excluded_deck_ids(cfg):
            return True
    except Exception:
        pass

    return False


def _pause_block(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """The pause-key half of every payload.

    It rides on the disabled payloads too: the sticky flag has to reach the JS
    even on a card aSFM isn't timing, or pausing on one card and moving to an
    excluded one would silently drop the hold.
    """
    global _auto_paused
    on = bool(cfg.get("enabled", True))
    key_on = on and bool(cfg.get("pause_key_enabled", True))
    button_on = on and bool(cfg.get("more_time_button", True))

    if _auto_paused and not (key_on or button_on):
        _auto_paused = False

    return {
        "pauseKey": str(cfg.get("pause_key") or "p").lower(),
        "pauseEnabled": key_on,
        "moreTimeButton": button_on,
        "autoPaused": _auto_paused,
    }


def question_payload(card) -> Dict[str, Any]:
    cfg = _get_cfg()
    off = {"enabled": False, **_pause_block(cfg)}
    if not cfg.get("enabled", True) or _excluded(card, cfg):
        return off
    if adaptive.is_new_card(card) and not cfg.get("enable_on_new", True):
        return off

    delay_ms = int(adaptive.reveal_delay_seconds(card, cfg) * 1000)
    return {
        "enabled": True,
        "delayMs": delay_ms,
        "showCountdown": bool(cfg.get("show_countdown", True)),
        "warn": bool(cfg.get("warning_sound", True)),
        "warnPercent": int(cfg.get("warning_at_percent", 75)),
        **_pause_block(cfg),
    }


# ----- hooks -----

def _on_will_set_content(web_content, context, *args, **kwargs) -> None:
    if isinstance(context, Reviewer):
        web_content.body += _INJECT


def _on_show_question(*args, **kwargs) -> None:
    card = mw.reviewer.card if mw.reviewer else None
    if not card:
        return
    _eval(f"window.ASFM && ASFM.onCard({json.dumps(question_payload(card))});")


def _on_show_answer(*args, **kwargs) -> None:
    payload = {"enabled": False, **_pause_block(_get_cfg())}
    _eval(f"window.ASFM && ASFM.onCard({json.dumps(payload)});")


def _on_js_message(handled, message: str, context, *args, **kwargs):
    if not isinstance(message, str) or not message.startswith(PYCMD_PREFIX):
        return handled

    action = message[len(PYCMD_PREFIX):]
    if action == "reveal":
        rv = mw.reviewer
        if rv and rv.card and rv.state == "question":
            rv._showAnswer()
        return (True, None)

    if action == "warn":
        _play_alert()
        return (True, None)

    if action.startswith("autopause:"):
        global _auto_paused
        _auto_paused = action.endswith("1")
        key = str(_get_cfg().get("pause_key") or "p").upper()
        tooltip(
            f"⏸ Auto-reveal paused — press {key} to resume" if _auto_paused
            else "▶ Auto-reveal resumed",
            period=1800,
        )
        return (True, None)

    return handled


def register() -> None:
    mw.addonManager.setWebExports(PACKAGE, r"web.*")
    gui_hooks.webview_will_set_content.append(_on_will_set_content)
    gui_hooks.reviewer_did_show_question.append(_on_show_question)
    gui_hooks.reviewer_did_show_answer.append(_on_show_answer)
    gui_hooks.webview_did_receive_js_message.append(_on_js_message)
    
    # Invalidate cache when user updates config via GUI
    if hasattr(gui_hooks, "addon_config_updated"):
        gui_hooks.addon_config_updated.append(_invalidate_config_cache)
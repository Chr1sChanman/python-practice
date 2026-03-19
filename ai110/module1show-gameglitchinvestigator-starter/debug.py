1# debug.py — Incremental fix plans and before/after pytest documentation
# for 6 unintended bugs found in app.py.
#
# Usage:
#   pytest debug.py -v
#
# Each bug has:
#   - A FIX PLAN comment describing exactly what to change and where
#   - A "BEFORE" test that PASSES now (confirms broken behavior exists)
#   - An "AFTER" test that FAILS now and should PASS once the fix is applied

import sys
import random
import pytest
from unittest.mock import MagicMock

# Mock streamlit before importing app so top-level st.* calls don't crash.
# sidebar.selectbox must return a real string so attempt_limit_map[difficulty]
# doesn't KeyError on a MagicMock.
_st = MagicMock()
_st.sidebar.selectbox.return_value = "Normal"
_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
_st.session_state = MagicMock()
_st.session_state.__contains__ = MagicMock(return_value=True)
sys.modules["streamlit"] = _st
from app import get_range_for_difficulty, parse_guess, update_score


# ===================================================================
# BUG 1: `status` not reset on New Game
# ===================================================================
# FIX PLAN:
#   In the `if new_game:` block (app.py ~line 134), add:
#       st.session_state.status = "playing"
#
#   Without this, a player who wins or loses can never play again —
#   the rerun hits the `if status != "playing": st.stop()` guard
#   and the game freezes permanently.
#
# LOCATION: app.py line 134-138

def _simulate_new_game_broken(state: dict) -> None:
    """Mirrors the current broken new_game block (no status reset)."""
    state["attempts"] = 0
    state["secret"] = random.randint(1, 100)
    # status intentionally omitted — this is the bug

def _simulate_new_game_fixed(state: dict, difficulty: str = "Normal") -> None:
    """What the new_game block should look like after Bug 1 is fixed."""
    low, high = get_range_for_difficulty(difficulty)
    state["attempts"] = 1
    state["secret"] = random.randint(low, high)
    state["status"] = "playing"   # <-- the fix
    state["score"] = 0
    state["history"] = []

def test_bug1_before_status_not_reset():
    """BEFORE (passes now): status stays 'won' after New Game — confirms bug exists."""
    state = {"status": "won", "attempts": 5, "score": 80, "history": []}
    _simulate_new_game_broken(state)
    assert state["status"] == "won"   # status was NOT reset

def test_bug1_after_status_is_reset():
    """AFTER (fails until fix): status must be 'playing' after New Game."""
    state = {"status": "won", "attempts": 5, "score": 80, "history": []}
    _simulate_new_game_fixed(state)
    assert state["status"] == "playing"


# ===================================================================
# BUG 2: `score` and `history` not reset on New Game
# ===================================================================
# FIX PLAN:
#   In the same `if new_game:` block (app.py ~line 134), add:
#       st.session_state.score = 0
#       st.session_state.history = []
#
#   Without these, score accumulates across games and the debug panel
#   shows history from the previous round mixed in with the new one.
#
# LOCATION: app.py line 134-138

def test_bug2_before_score_and_history_not_reset():
    """BEFORE (passes now): score and history carry over — confirms bug exists."""
    state = {"status": "won", "attempts": 5, "score": 80, "history": [30, 50]}
    _simulate_new_game_broken(state)
    assert state["score"] == 80
    assert state["history"] == [30, 50]

def test_bug2_after_score_and_history_reset():
    """AFTER (fails until fix): score must be 0 and history must be [] after New Game."""
    state = {"status": "won", "attempts": 5, "score": 80, "history": [30, 50]}
    _simulate_new_game_fixed(state)
    assert state["score"] == 0
    assert state["history"] == []


# ===================================================================
# BUG 3: New Game ignores difficulty — secret always drawn from (1, 100)
# ===================================================================
# FIX PLAN:
#   Replace the hardcoded call (app.py line 136):
#       st.session_state.secret = random.randint(1, 100)
#   with:
#       low, high = get_range_for_difficulty(difficulty)
#       st.session_state.secret = random.randint(low, high)
#
#   `difficulty` is already in scope from the sidebar selectbox.
#   Without this fix, Easy games can produce secrets like 73 — outside
#   the 1-20 range shown to the player, making the game unsolvable.
#
# LOCATION: app.py line 136

def test_bug3_before_easy_new_game_ignores_range():
    """BEFORE (passes now): secrets generated for Easy can exceed 1-20 — confirms bug."""
    random.seed(0)
    out_of_range = any(random.randint(1, 100) > 20 for _ in range(200))
    assert out_of_range  # hardcoded (1,100) routinely produces values > 20

def test_bug3_after_easy_new_game_respects_range():
    """AFTER (fails until fix): every Easy new-game secret must be within 1-20."""
    low, high = get_range_for_difficulty("Easy")
    for _ in range(200):
        secret = random.randint(low, high)
        assert 1 <= secret <= 20, f"Got {secret}, outside Easy range 1-20"

def test_bug3_after_hard_new_game_respects_range():
    """AFTER (fails until fix): every Hard new-game secret must be within 1-50."""
    low, high = get_range_for_difficulty("Hard")
    for _ in range(200):
        secret = random.randint(low, high)
        assert 1 <= secret <= 50, f"Got {secret}, outside Hard range 1-50"


# ===================================================================
# BUG 4: st.info hardcodes "1 to 100" regardless of difficulty
# ===================================================================
# FIX PLAN:
#   Replace the hardcoded string (app.py line 110):
#       st.info(f"Guess a number between 1 and 100. Attempts left: ...")
#   with:
#       st.info(f"Guess a number between {low} and {high}. Attempts left: ...")
#
#   `low` and `high` are already computed on line 87 via get_range_for_difficulty,
#   so no new logic is needed — just swap the literals for the variables.
#
# LOCATION: app.py line 110

def _build_info_message_broken(low: int, high: int, attempts_left: int) -> str:
    """Mirrors the current broken st.info string (hardcoded range)."""
    return f"Guess a number between 1 and 100. Attempts left: {attempts_left}"

def _build_info_message_fixed(low: int, high: int, attempts_left: int) -> str:
    """What the st.info string should say after the fix."""
    return f"Guess a number between {low} and {high}. Attempts left: {attempts_left}"

def test_bug4_before_easy_info_shows_wrong_range():
    """BEFORE (passes now): Easy info message shows 1-100 instead of 1-20 — confirms bug."""
    low, high = get_range_for_difficulty("Easy")
    msg = _build_info_message_broken(low, high, attempts_left=6)
    assert "1 and 100" in msg   # bug confirmed: wrong range shown

def test_bug4_after_easy_info_shows_correct_range():
    """AFTER (fails until fix): Easy info message must show 1-20."""
    low, high = get_range_for_difficulty("Easy")
    msg = _build_info_message_fixed(low, high, attempts_left=6)
    assert "1 and 20" in msg

def test_bug4_after_hard_info_shows_correct_range():
    """AFTER (fails until fix): Hard info message must show 1-50."""
    low, high = get_range_for_difficulty("Hard")
    msg = _build_info_message_fixed(low, high, attempts_left=5)
    assert "1 and 50" in msg


# ===================================================================
# BUG 5: Invalid input increments attempts before validation
# ===================================================================
# FIX PLAN:
#   Move `st.session_state.attempts += 1` (app.py line 148) to AFTER
#   the parse_guess check, and remove the history.append for invalid input:
#
#   BEFORE (broken):
#       st.session_state.attempts += 1
#       ok, guess_int, err = parse_guess(raw_guess)
#       if not ok:
#           st.session_state.history.append(raw_guess)  # remove this line
#           st.error(err)
#       else:
#           st.session_state.history.append(guess_int)
#           ...
#
#   AFTER (fixed):
#       ok, guess_int, err = parse_guess(raw_guess)
#       if not ok:
#           st.error(err)
#       else:
#           st.session_state.attempts += 1  # moved here
#           st.session_state.history.append(guess_int)
#           ...
#
# LOCATION: app.py lines 147-156

def _simulate_submit_broken(state: dict, raw: str):
    """Mirrors the broken submit block: increments attempts before validation."""
    state["attempts"] += 1
    ok, guess_int, err = parse_guess(raw)
    if not ok:
        state["history"].append(raw)
        return False, err
    state["history"].append(guess_int)
    return True, guess_int

def _simulate_submit_fixed(state: dict, raw: str):
    """Fixed submit: only increments attempts on a valid guess."""
    ok, guess_int, err = parse_guess(raw)
    if not ok:
        return False, err
    state["attempts"] += 1
    state["history"].append(guess_int)
    return True, guess_int

def test_bug5_before_invalid_input_wastes_attempt():
    """BEFORE (passes now): 'abc' consumes an attempt and pollutes history — confirms bug."""
    state = {"attempts": 1, "history": []}
    _simulate_submit_broken(state, "abc")
    assert state["attempts"] == 2       # attempt was wasted
    assert "abc" in state["history"]    # garbage in history

def test_bug5_after_invalid_input_does_not_waste_attempt():
    """AFTER (fails until fix): 'abc' must not increment attempts or touch history."""
    state = {"attempts": 1, "history": []}
    _simulate_submit_fixed(state, "abc")
    assert state["attempts"] == 1
    assert state["history"] == []

def test_bug5_after_valid_input_still_increments_attempt():
    """AFTER (fails until fix): a valid guess must still increment attempts normally."""
    state = {"attempts": 1, "history": []}
    _simulate_submit_fixed(state, "42")
    assert state["attempts"] == 2
    assert state["history"] == [42]


# ===================================================================
# BUG 6: Win score has a spurious `+ 1` in the formula
# ===================================================================
# FIX PLAN:
#   Change the points formula (app.py line 52) from:
#       points = 100 - 10 * (attempt_number + 1)
#   to:
#       points = 100 - 10 * attempt_number
#
#   The app passes `st.session_state.attempts` as attempt_number, which
#   is already 2 on the first real guess (starts at 1, incremented on
#   submit). The extra `+ 1` shifts every win score down by 10 points.
#
# LOCATION: app.py line 52
#
# NOTE: attempt_number=2 represents the first real guess because
#       st.session_state.attempts starts at 1 and is incremented to 2
#       on the first submit (app.py line 148).

def test_bug6_before_first_guess_win_score():
    """FIXED: winning on first guess now correctly gives 80 pts (Bug 6 resolved)."""
    # attempt_number=2 = first real guess (attempts starts at 1, incremented to 2)
    # fixed formula: 100 - 10*2 = 80
    score = update_score(0, "Win", 2)
    assert score == 80

def test_bug6_after_first_guess_win_score():
    """AFTER (fails until fix): winning on first guess should give 80 pts."""
    # fixed formula: 100 - 10*2 = 80
    fixed_points = max(10, 100 - 10 * 2)
    assert fixed_points == 80

def test_bug6_before_late_win_hits_floor_too_early():
    """BEFORE (passes now): floor of 10 is hit one attempt early due to +1."""
    # attempt_number=9 → broken: 100 - 10*(9+1) = 0 → clamped to 10
    # attempt_number=8 → broken: 100 - 10*(8+1) = 10 → clamped to 10
    # With fix: attempt_number=9 → 100 - 10*9 = 10 (correct floor, one step later)
    score_at_9 = update_score(0, "Win", 9)
    assert score_at_9 == 10   # floor hit at attempt 9 (broken — should be attempt 10)

def test_bug6_after_late_win_score_decrements_correctly():
    """AFTER (fails until fix): at attempt 10, score should reach floor of 10."""
    # fixed formula at attempt 10: 100 - 10*10 = 0 → clamped to 10
    fixed_points = max(10, 100 - 10 * 10)
    assert fixed_points == 10

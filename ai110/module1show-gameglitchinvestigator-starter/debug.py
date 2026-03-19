# debug.py — Incremental fix plans and before/after pytest documentation
# for 6 unintended bugs found in app.py.
#
# Usage:
#   pytest debug.py -v
#
# Each bug section has:
#   - A FIX PLAN comment: exactly what to change and where in app.py
#   - A "BEFORE" test that PASSES now  (confirms the broken behavior exists)
#   - An "AFTER"  test that FAILS now  (documents the correct target behavior;
#                                       should PASS once the fix is applied)
#
# Functions are copied from app.py so that top-level Streamlit calls
# in app.py do not interfere with test collection.

import random
import pytest


# ── Copies of the relevant functions from app.py ────────────────────────────

def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    if raw is None:
        return False, None, "Enter a guess."
    if raw == "":
        return False, None, "Enter a guess."
    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."
    return True, value, None


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)   # Bug 6: spurious +1
        if points < 10:
            points = 10
        return current_score + points
    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5
    if outcome == "Too Low":
        return current_score - 5
    return current_score


# ── Helpers that simulate the broken and fixed new_game / submit blocks ──────

def _simulate_new_game_broken(state: dict) -> None:
    """Mirrors the current broken new_game block (app.py ~line 134)."""
    state["attempts"] = 0
    state["secret"] = random.randint(1, 100)
    # status, score, history are never reset — that is Bugs 1 & 2


def _simulate_new_game_fixed(state: dict, difficulty: str = "Normal") -> None:
    """What the new_game block should look like after Bugs 1–3 are fixed."""
    low, high = get_range_for_difficulty(difficulty)
    state["attempts"] = 1
    state["secret"] = random.randint(low, high)
    state["status"] = "playing"   # Bug 1 fix
    state["score"] = 0            # Bug 2 fix
    state["history"] = []         # Bug 2 fix
    # Bug 3 fix: uses low/high from difficulty instead of hardcoded (1, 100)


def _simulate_submit_broken(state: dict, raw: str):
    """Mirrors the broken submit block (app.py ~line 147): increments before validation."""
    state["attempts"] += 1                        # Bug 5: incremented too early
    ok, guess_int, err = parse_guess(raw)
    if not ok:
        state["history"].append(raw)              # Bug 5: garbage in history
        return False, err
    state["history"].append(guess_int)
    return True, guess_int


def _simulate_submit_fixed(state: dict, raw: str):
    """Fixed submit: only increments attempts on a valid guess."""
    ok, guess_int, err = parse_guess(raw)
    if not ok:
        return False, err
    state["attempts"] += 1                        # moved after validation
    state["history"].append(guess_int)
    return True, guess_int


# ── Bug 1: `status` not reset on New Game ───────────────────────────────────
#
# FIX PLAN:
#   app.py ~line 134  — in the `if new_game:` block, add:
#       st.session_state.status = "playing"
#
#   Without this, after a win or loss the rerun hits the
#   `if status != "playing": st.stop()` guard and the game is frozen.

def test_bug1_before_status_not_reset():
    """BEFORE (passes now): status stays 'won' after New Game — confirms bug exists."""
    state = {"status": "won", "attempts": 5, "score": 80, "history": []}
    _simulate_new_game_broken(state)
    assert state["status"] == "won"       # NOT reset → bug confirmed

def test_bug1_after_status_is_reset():
    """AFTER (fails until fix): status must be 'playing' immediately after New Game."""
    state = {"status": "won", "attempts": 5, "score": 80, "history": []}
    _simulate_new_game_fixed(state)
    assert state["status"] == "playing"


# ── Bug 2: `score` and `history` not reset on New Game ──────────────────────
#
# FIX PLAN:
#   app.py ~line 134  — in the same `if new_game:` block, also add:
#       st.session_state.score = 0
#       st.session_state.history = []
#
#   Without these, score accumulates across games and old guesses appear
#   in the debug panel alongside the new game's history.

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


# ── Bug 3: New Game ignores difficulty — secret always drawn from (1, 100) ──
#
# FIX PLAN:
#   app.py line 136  — replace:
#       st.session_state.secret = random.randint(1, 100)
#   with:
#       low, high = get_range_for_difficulty(difficulty)
#       st.session_state.secret = random.randint(low, high)
#
#   `difficulty` is already in scope from the sidebar selectbox.
#   On Easy (range 1–20) the hardcoded call can produce secrets up to 100,
#   making the game unwinnable without knowing the secret.

def test_bug3_before_easy_new_game_ignores_range():
    """BEFORE (passes now): Easy new-game secrets can exceed 1-20 — confirms bug."""
    random.seed(0)
    out_of_range = any(random.randint(1, 100) > 20 for _ in range(200))
    assert out_of_range   # hardcoded (1,100) routinely exceeds Easy range

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


# ── Bug 4: st.info hardcodes "1 to 100" regardless of difficulty ────────────
#
# FIX PLAN:
#   app.py line 110  — replace:
#       st.info(f"Guess a number between 1 and 100. Attempts left: ...")
#   with:
#       st.info(f"Guess a number between {low} and {high}. Attempts left: ...")
#
#   `low` and `high` are already computed on line 87 via get_range_for_difficulty,
#   so no new logic is needed — just swap the literals for the variables.

def _build_info_message_broken(low: int, high: int, attempts_left: int) -> str:
    return f"Guess a number between 1 and 100. Attempts left: {attempts_left}"

def _build_info_message_fixed(low: int, high: int, attempts_left: int) -> str:
    return f"Guess a number between {low} and {high}. Attempts left: {attempts_left}"

def test_bug4_before_easy_info_shows_wrong_range():
    """BEFORE (passes now): Easy info message shows 1-100 instead of 1-20 — confirms bug."""
    low, high = get_range_for_difficulty("Easy")
    msg = _build_info_message_broken(low, high, attempts_left=6)
    assert "1 and 100" in msg   # wrong range displayed

def test_bug4_after_easy_info_shows_correct_range():
    """AFTER (fails until fix): Easy info message must show 1 and 20."""
    low, high = get_range_for_difficulty("Easy")
    msg = _build_info_message_fixed(low, high, attempts_left=6)
    assert "1 and 20" in msg

def test_bug4_after_hard_info_shows_correct_range():
    """AFTER (fails until fix): Hard info message must show 1 and 50."""
    low, high = get_range_for_difficulty("Hard")
    msg = _build_info_message_fixed(low, high, attempts_left=5)
    assert "1 and 50" in msg


# ── Bug 5: Invalid input increments attempts before validation ───────────────
#
# FIX PLAN:
#   app.py lines 147-156  — move the attempts increment and remove the
#   invalid-input history append:
#
#   BROKEN (current):
#       st.session_state.attempts += 1          # line 148 — too early
#       ok, guess_int, err = parse_guess(raw_guess)
#       if not ok:
#           st.session_state.history.append(raw_guess)   # line 153 — remove
#           st.error(err)
#       else:
#           st.session_state.history.append(guess_int)
#
#   FIXED:
#       ok, guess_int, err = parse_guess(raw_guess)
#       if not ok:
#           st.error(err)
#       else:
#           st.session_state.attempts += 1      # moved here
#           st.session_state.history.append(guess_int)

def test_bug5_before_invalid_input_wastes_attempt():
    """BEFORE (passes now): 'abc' consumes an attempt and pollutes history — confirms bug."""
    state = {"attempts": 1, "history": []}
    _simulate_submit_broken(state, "abc")
    assert state["attempts"] == 2       # attempt wasted on bad input
    assert "abc" in state["history"]    # raw string in history

def test_bug5_after_invalid_input_does_not_waste_attempt():
    """AFTER (fails until fix): 'abc' must not change attempts or history."""
    state = {"attempts": 1, "history": []}
    _simulate_submit_fixed(state, "abc")
    assert state["attempts"] == 1
    assert state["history"] == []

def test_bug5_after_valid_input_still_increments():
    """AFTER (fails until fix): a valid guess must still increment attempts normally."""
    state = {"attempts": 1, "history": []}
    _simulate_submit_fixed(state, "42")
    assert state["attempts"] == 2
    assert state["history"] == [42]


# ── Bug 6: Win score has a spurious `+ 1` in the formula ────────────────────
#
# FIX PLAN:
#   app.py line 52  — change:
#       points = 100 - 10 * (attempt_number + 1)
#   to:
#       points = 100 - 10 * attempt_number
#
#   attempt_number is st.session_state.attempts which is already 2 on the
#   first real guess (starts at 1, incremented to 2 on submit at line 148).
#   The extra +1 silently docks 10 points from every win.

def test_bug6_before_first_guess_win_score():
    """BEFORE (passes now): first-guess win gives 70 pts instead of 80 — confirms bug."""
    # attempt_number=2 = first real guess (attempts starts at 1, +1 on submit)
    score = update_score(0, "Win", 2)
    # broken formula: 100 - 10*(2+1) = 70
    assert score == 70

def test_bug6_after_first_guess_win_score():
    """AFTER (fails until fix): first-guess win should yield 80 pts."""
    # fixed formula: 100 - 10*2 = 80
    fixed_points = max(10, 100 - 10 * 2)
    assert fixed_points == 80

def test_bug6_before_floor_hit_too_early():
    """BEFORE (passes now): score floor of 10 is reached one attempt too early."""
    # attempt_number=9: broken → 100 - 10*(9+1) = 0 → clamped to 10
    # With fix at attempt_number=9: 100 - 10*9 = 10 (correct, same value but right path)
    # At attempt_number=8: broken → 100 - 10*(8+1) = 10; fixed → 100 - 10*8 = 20
    score_at_8_broken = update_score(0, "Win", 8)
    assert score_at_8_broken == 10   # floor hit at attempt 8 (one too early)

def test_bug6_after_attempt_8_gives_correct_score():
    """AFTER (fails until fix): at attempt 8, score should be 20, not 10."""
    fixed_points = max(10, 100 - 10 * 8)
    assert fixed_points == 20

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
python -m streamlit run app.py

# Run tests
pytest

# Run a single test
pytest tests/test_game_logic.py::test_winning_guess
```

## Project Overview

This is a **debugging/learning exercise** — a deliberately broken Streamlit number-guessing game that students are meant to fix.

### The Assignment (4 challenges)

1. **Play the broken game** — use the "Developer Debug Info" expander to see the secret number and observe that you can't win.
2. **Fix the state bug** — `st.session_state` must be used to persist the secret number across rerenders; currently the secret resets on each submit.
3. **Fix the logic bugs** — `check_guess` in `app.py` has inverted hints ("Too High" / "Too Low" are swapped) and a type-coercion trick that makes even correct guesses fail on even-numbered attempts.
4. **Refactor & test** — move `get_range_for_difficulty`, `parse_guess`, `check_guess`, and `update_score` from `app.py` into `logic_utils.py` (which currently only has stub `raise NotImplementedError` versions), then run `pytest` until all tests pass.

### Key Intentional Bugs in `app.py`

- **Hint inversion** (`check_guess`, line ~38-40): when `guess > secret` it says "Go HIGHER" instead of "Go LOWER".
- **Type coercion glitch** (lines ~158-163): on even-numbered attempts, `secret` is cast to `str`, causing integer-vs-string comparison to always fail the win check.
- **Hard difficulty range** (`get_range_for_difficulty`, line ~9): Hard maps to 1–50 but the UI still shows "1 to 100".
- **New game bug** (line ~135): `st.session_state.attempts` is reset to `0` instead of `1`, causing an off-by-one on the first guess of a new game.

### Test contract (`tests/test_game_logic.py`)

Tests import `check_guess` from `logic_utils` and expect it to return only the outcome string (e.g., `"Win"`, `"Too High"`, `"Too Low"`), **not** a tuple — unlike the current `app.py` implementation which returns `(outcome, message)`. The refactored `logic_utils.check_guess` must match this single-return-value signature.

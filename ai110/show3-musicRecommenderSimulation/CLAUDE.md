# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the CLI app
python -m src.main

# Run all tests
pytest

# Run a single test
pytest tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score
```

## Architecture

This is an AI110 course project — a music recommendation system simulation. The project is intentionally incomplete (skeleton code); the student implements the scoring logic.

**Two parallel APIs live in `src/recommender.py`:**

1. **OOP API** (`Song` dataclass + `UserProfile` dataclass + `Recommender` class) — used by the test suite directly
2. **Functional API** (`load_songs()` + `recommend_songs()`) — used by `src/main.py`

`src/main.py` is the CLI entry point: it calls `load_songs("data/songs.csv")` to get a list of song dicts, builds a sample `user_prefs` dict, then calls `recommend_songs(user_prefs, songs, k=5)` which should return `(song_dict, score, explanation)` tuples.

**Scoring contract (what tests expect):**
- `Recommender.recommend(user, k)` returns top-k `Song` objects ranked by score — a pop/happy/high-energy song should rank above a lofi/chill song for a pop-loving user profile.
- `Recommender.explain_recommendation(user, song)` returns a non-empty string.
- `recommend_songs()` returns a list of `(dict, float, str)` tuples (song, score, explanation).

**Data:** `data/songs.csv` has 10 songs with features: `genre`, `mood`, `energy` (0–1), `tempo_bpm`, `valence`, `danceability`, `acousticness`.

**Documentation to fill in:** `README.md` and `model_card.md` are templates — the student must fill in their design choices, experiments, and reflections.

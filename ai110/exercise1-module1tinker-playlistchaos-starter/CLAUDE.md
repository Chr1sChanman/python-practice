# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
pip install -r requirements.txt
streamlit run app.py
```

There are no tests. Verify behavior manually by interacting with the Streamlit UI.

## Architecture

Two files with a clean separation of concerns:

- **`playlist_logic.py`** — All business logic. Pure Python, no Streamlit imports. Contains: song normalization (`normalize_song`), mood classification (`classify_song`), playlist building (`build_playlists`), merging (`merge_playlists`), stats (`compute_playlist_stats`), search (`search_songs`), lucky pick (`lucky_pick`), and history summary (`history_summary`). Also defines the `Song` and `PlaylistMap` type aliases and `DEFAULT_PROFILE`.

- **`app.py`** — Streamlit UI only. Manages `st.session_state` (keys: `songs`, `profile`, `history`). Calls into `playlist_logic` for all data processing. The `main()` flow: init state → render sidebar (profile + add song + manage data) → build playlists → render tabs/lucky/stats/history.

### Data model

A `Song` is a plain `dict` with keys: `title`, `artist`, `genre`, `energy` (int 1–10), `tags` (list of str). After `build_playlists`, a `mood` key (`"Hype"`, `"Chill"`, or `"Mixed"`) is added. A `PlaylistMap` is `{"Hype": [...], "Chill": [...], "Mixed": [...]}`.

### Mood classification logic (`classify_song`)

- **Hype**: `energy >= hype_min_energy` AND (`genre == favorite_genre` OR genre contains a hype keyword like "rock", "punk", "party")
- **Chill**: `energy <= chill_max_energy` OR the *title* contains a chill keyword ("lofi", "ambient", "sleep") — note: the keyword check is on title, not genre
- **Mixed**: everything else

### Known intentional bugs (this is a debugging exercise)

This project is intentionally broken in several places for students to find and fix:

1. **`search_songs`** (`playlist_logic.py:171`): condition is `value in q` (field value contained in query) instead of `q in value` (query contained in field value) — causes search to mostly return nothing
2. **`compute_playlist_stats`** (`playlist_logic.py:119`): `total = len(hype)` should be `len(all_songs)` — makes `hype_ratio` always 1.0 when hype is non-empty
3. **`compute_playlist_stats`** (`playlist_logic.py:124`): `avg_energy` sums only hype songs' energy but divides by all songs
4. **`classify_song`** (`playlist_logic.py:74`): `is_chill_keyword` checks `title` for chill keywords instead of `genre`
5. **`random_choice_or_none`** (`playlist_logic.py:196`): calls `random.choice(songs)` on a potentially empty list — will raise `IndexError`
6. **`lucky_pick`** (`playlist_logic.py:187`): "any" mode excludes `Mixed` playlist songs

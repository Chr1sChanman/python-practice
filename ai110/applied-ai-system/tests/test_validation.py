"""
Phase 2 tests: runtime validation guardrails and structured JSONL logging.
"""
import json
import warnings
from pathlib import Path

import pytest

from src.recommender import UserProfile, recommend_songs, load_songs


# Hard violations: must raise ValueError 
def test_target_energy_out_of_range_raises():
    user = UserProfile(target_energy=1.5)
    with pytest.raises(ValueError, match="target_energy"):
        user.validate()


def test_negative_genre_weight_raises():
    user = UserProfile(favorite_genres={"pop": -0.5})
    with pytest.raises(ValueError, match="favorite_genres"):
        user.validate()


def test_zero_tempo_raises():
    user = UserProfile(target_tempo_bpm=0)
    with pytest.raises(ValueError, match="target_tempo_bpm"):
        user.validate()


def test_recommend_songs_propagates_validation_error(tmp_path, monkeypatch):
    """recommend_songs must reject invalid profiles before scoring."""
    monkeypatch.chdir(tmp_path)
    songs = load_songs(str(Path(__file__).parent.parent / "data" / "songs.csv"))
    bad_user = UserProfile(target_energy=99.0)
    with pytest.raises(ValueError):
        recommend_songs(bad_user, songs, k=3)


# Soft contradictions: warn but do not raise
def test_like_dislike_overlap_warns_but_does_not_raise():
    user = UserProfile(liked_song_ids=[3, 7], disliked_song_ids=[7])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        warns = user.validate()
    assert any("7" in w for w in warns), "warning list should mention the overlapping id"
    assert any(
        issubclass(item.category, UserWarning) for item in caught
    ), "a UserWarning should have been emitted"


# Logging: every call appends one JSONL line 
def test_recommend_songs_writes_jsonl_log(tmp_path, monkeypatch):
    """A successful recommend_songs call appends one valid JSON line to the log."""
    monkeypatch.chdir(tmp_path)
    songs = load_songs(str(Path(__file__).parent.parent / "data" / "songs.csv"))
    user = UserProfile(
        favorite_genres={"pop": 1.0},
        favorite_moods={"happy": 1.0},
        target_energy=0.8,
    )

    # Force a fresh logger handler bound to tmp_path/logs/recommender.jsonl
    import logging
    logging.getLogger("recommender").handlers.clear()

    recommend_songs(user, songs, k=3)

    log_path = tmp_path / "logs" / "recommender.jsonl"
    assert log_path.exists(), "log file should be created"
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 1, "exactly one line per recommend_songs call"

    record = json.loads(lines[0])
    assert record["event"] == "recommend"
    assert record["k"] == 3
    assert "top_ids" in record and len(record["top_ids"]) == 3
    assert "latency_ms" in record
    assert "profile_hash" in record

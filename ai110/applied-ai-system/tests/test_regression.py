"""
Phase 4 tests: golden regression snapshots.

For every profile in data/eval_profiles.json, we pin the top-5 recommendation
as a list of ``(id, round(score, 4))`` pairs into tests/_golden/<slug>.json.
If the recommender's behaviour shifts (intentional or not), these tests fail
with a readable diff.

Escape hatch: set ``UPDATE_GOLDEN=1`` to overwrite the snapshots deliberately.

    UPDATE_GOLDEN=1 pytest tests/test_regression.py
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import List, Tuple

import pytest

from src.config import ScoringConfig
from src.recommender import UserProfile, load_songs, recommend_songs


REPO_ROOT = Path(__file__).parent.parent
GOLDEN_DIR = Path(__file__).parent / "_golden"
EVAL_PATH = REPO_ROOT / "data" / "eval_profiles.json"
SONGS_PATH = REPO_ROOT / "data" / "songs.csv"


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _current_top5(profile_dict: dict) -> List[Tuple[int, float]]:
    user = UserProfile(**profile_dict)
    songs = load_songs(str(SONGS_PATH))
    ranked = recommend_songs(user, songs, k=5, config=ScoringConfig())
    return [(song["id"], round(score, 4)) for song, score, _ in ranked]


def _eval_profiles() -> List[Tuple[str, dict]]:
    raw = json.loads(EVAL_PATH.read_text())
    return [(entry["name"], entry["profile"]) for entry in raw["profiles"]]


# Collect all profiles once so pytest can parametrize over them.
@pytest.mark.parametrize(
    "profile_name,profile_dict",
    _eval_profiles(),
    ids=[name for name, _ in _eval_profiles()],
)
def test_top5_matches_golden(profile_name: str, profile_dict: dict):
    """Compare current top-5 against the pinned snapshot."""
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    golden_path = GOLDEN_DIR / f"{_slug(profile_name)}.json"
    current = _current_top5(profile_dict)

    if os.environ.get("UPDATE_GOLDEN") == "1":
        golden_path.write_text(
            json.dumps(
                {"profile": profile_name, "top5": current},
                indent=2,
            )
            + "\n"
        )
        return

    if not golden_path.exists():
        pytest.fail(
            f"missing golden snapshot at {golden_path}. "
            f"Run `UPDATE_GOLDEN=1 pytest tests/test_regression.py` "
            f"to create it."
        )

    expected = json.loads(golden_path.read_text())["top5"]
    # JSON round-trips tuples as lists; coerce for comparison.
    expected = [tuple(item) for item in expected]
    assert current == expected, (
        f"top-5 for {profile_name} drifted.\n"
        f"  current:  {current}\n"
        f"  expected: {expected}\n"
        f"If intentional, rerun with UPDATE_GOLDEN=1 to re-record."
    )

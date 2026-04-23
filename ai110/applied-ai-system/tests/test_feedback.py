"""
Phase 6 tests: feedback parser + interactive loop integration.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.feedback import (
    AdjustTarget,
    DislikeSong,
    Done,
    LikeSong,
    Unknown,
    parse_feedback,
)
from src.main import run_interactive


# parse_feedback unit cases
def test_parse_like():
    assert parse_feedback("like 3") == LikeSong(song_id=3)


def test_parse_dislike():
    assert parse_feedback("dislike 5") == DislikeSong(song_id=5)


def test_parse_done_synonyms():
    for word in ("done", "quit", "exit", "q", "  Done  "):
        assert isinstance(parse_feedback(word), Done)


def test_parse_more_energy():
    a = parse_feedback("more energy")
    assert isinstance(a, AdjustTarget)
    assert a.field == "target_energy"
    assert a.delta > 0


def test_parse_less_acoustic_alias():
    a = parse_feedback("less acoustic")
    assert isinstance(a, AdjustTarget)
    assert a.field == "target_acousticness"
    assert a.delta < 0


def test_parse_unknown_returns_hint():
    a = parse_feedback("delete database")
    assert isinstance(a, Unknown)
    assert a.hint and "like" in a.hint


def test_parse_like_with_non_integer_id():
    a = parse_feedback("like banana")
    assert isinstance(a, Unknown)


def test_parse_empty():
    assert isinstance(parse_feedback(""), Unknown)


# Interactive loop integration
class _Driver:
    """Records output and feeds prepared input lines to run_interactive."""

    def __init__(self, inputs: list[str]):
        self._inputs = list(inputs)
        self.output: list[str] = []

    def input_fn(self, prompt: str) -> str:
        if not self._inputs:
            raise EOFError
        return self._inputs.pop(0)

    def output_fn(self, line: str) -> None:
        self.output.append(line)


def test_interactive_accepts_like_then_done(tmp_path):
    log_path = tmp_path / "agent.jsonl"
    driver = _Driver(["like 3", "done"])
    profile = run_interactive(
        starting_profile_name="High-Energy Pop",
        input_fn=driver.input_fn,
        output_fn=driver.output_fn,
        log_path=str(log_path),
    )
    assert 3 in profile.liked_song_ids

    # Logs should record start, accepted, done.
    lines = [json.loads(line) for line in log_path.read_text().strip().splitlines()]
    events = [r["event"] for r in lines]
    assert "interactive_start" in events
    assert "interactive_accepted" in events
    assert "interactive_done" in events


def test_interactive_rejects_unknown_song_id(tmp_path):
    log_path = tmp_path / "agent.jsonl"
    driver = _Driver(["like 999", "done"])
    profile = run_interactive(
        starting_profile_name="Chill Lofi",
        input_fn=driver.input_fn,
        output_fn=driver.output_fn,
        log_path=str(log_path),
    )
    assert 999 not in profile.liked_song_ids

    lines = [json.loads(line) for line in log_path.read_text().strip().splitlines()]
    events = [r["event"] for r in lines]
    assert "interactive_rejected" in events
    # rejection reason should mention the missing song id
    rejection = next(r for r in lines if r["event"] == "interactive_rejected")
    assert "999" in rejection["reason"]


def test_interactive_does_not_crash_on_garbage(tmp_path):
    log_path = tmp_path / "agent.jsonl"
    driver = _Driver(["nonsense", "more flibbertigibbet", "done"])
    run_interactive(
        starting_profile_name="High-Energy Pop",
        input_fn=driver.input_fn,
        output_fn=driver.output_fn,
        log_path=str(log_path),
    )
    lines = [json.loads(line) for line in log_path.read_text().strip().splitlines()]
    rejections = [r for r in lines if r["event"] == "interactive_rejected"]
    assert len(rejections) >= 2


def test_interactive_adjust_more_energy_changes_profile(tmp_path):
    log_path = tmp_path / "agent.jsonl"
    driver = _Driver(["less energy", "done"])
    profile = run_interactive(
        starting_profile_name="High-Energy Pop",
        input_fn=driver.input_fn,
        output_fn=driver.output_fn,
        log_path=str(log_path),
    )
    # original target_energy was 0.86; after one "less" it should drop by 0.10
    assert profile.target_energy == pytest.approx(0.76, abs=1e-6)

"""
Phase 5 tests: WeightTuningAgent contract.

- The agent never produces an out-of-bounds ScoringConfig.
- Starting from a deliberately bad config, the agent improves mean_ndcg.
- Two runs with the same seed produce identical step logs.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.agent import WEIGHT_BOUNDS, WeightTuningAgent
from src.config import ScoringConfig


# Bounds invariant
def test_agent_never_produces_out_of_bounds_config(tmp_path):
    """Every after-config the agent emits must respect WEIGHT_BOUNDS."""
    agent = WeightTuningAgent(
        seed=1,
        step_size=5.0,  # large to push toward bounds
        log_path=str(tmp_path / "agent.jsonl"),
    )
    history = agent.run(budget=20)
    assert history, "agent should run at least one iteration"

    for step in history:
        for weight_name, (lo, hi) in WEIGHT_BOUNDS.items():
            value = getattr(step.after, weight_name)
            assert lo <= value <= hi, (
                f"step {step.iteration}: {weight_name}={value} "
                f"outside [{lo}, {hi}]"
            )


# Improvement on a bad starting config
def test_agent_improves_zeroed_starting_config(tmp_path):
    """A near-zero config should be improved within the budget."""
    bad = ScoringConfig(
        w_genre=0.0, w_mood=0.0, w_energy=0.0, w_tempo=0.0,
        w_valence=0.0, w_dance=0.0, w_acoustic=0.0, w_artist=0.0,
        w_liked=0.0, w_disliked=0.0,
    )
    agent = WeightTuningAgent(
        seed=0,
        step_size=1.0,
        starting_config=bad,
        patience=20,  # don't early-stop while exploring from cold start
        log_path=str(tmp_path / "agent.jsonl"),
    )
    history = agent.run(budget=20)
    starting_ndcg = history[0].report_before.aggregate["mean_ndcg"]
    final = bad
    for s in history:
        if s.accepted:
            final = s.after
    final_report = agent.check(final)
    assert final_report.aggregate["mean_ndcg"] > starting_ndcg, (
        f"expected improvement; starting={starting_ndcg:.4f}, "
        f"final={final_report.aggregate['mean_ndcg']:.4f}"
    )


# Reproducibility
def _run_steps(tmp_path: Path, seed: int, log_name: str) -> list[dict]:
    log_path = tmp_path / log_name
    agent = WeightTuningAgent(seed=seed, log_path=str(log_path))
    agent.run(budget=10)
    lines = log_path.read_text().strip().splitlines()
    return [json.loads(line) for line in lines if json.loads(line)["event"] == "agent_step"]


def test_same_seed_yields_identical_step_log(tmp_path):
    a = _run_steps(tmp_path, seed=42, log_name="run_a.jsonl")
    b = _run_steps(tmp_path, seed=42, log_name="run_b.jsonl")
    assert len(a) == len(b)
    for x, y in zip(a, b):
        # ts will differ; everything else should match exactly
        x.pop("ts", None)
        y.pop("ts", None)
        assert x == y


def test_different_seeds_diverge(tmp_path):
    a = _run_steps(tmp_path, seed=1, log_name="seed_1.jsonl")
    b = _run_steps(tmp_path, seed=2, log_name="seed_2.jsonl")
    a_actions = [step["action"] for step in a]
    b_actions = [step["action"] for step in b]
    assert a_actions != b_actions, "different seeds should produce different action sequences"

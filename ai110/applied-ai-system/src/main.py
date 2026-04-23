"""
Command line entry point for the music recommender.

Three modes:

    python -m src.main                  # demo: 5 named profiles
    python -m src.main --tune           # demo, but using the tuned ScoringConfig
    python -m src.main --interactive    # human-in-the-loop feedback session

In --tune mode the tuned weights are loaded from evidence/tuned_config.json
(produced by `python -m src.agent --save-config evidence/tuned_config.json`).
If that file does not exist, the agent is run on the fly first.
"""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from src.config import ScoringConfig
from src.feedback import (
    AdjustTarget,
    DislikeSong,
    Done,
    LikeSong,
    Unknown,
    parse_feedback,
)
from src.logging_utils import get_logger, log_event
from src.recommender import (
    UserProfile,
    load_songs,
    recommend_songs,
    score_song,
    Song,
)


# Profile catalog (the 5 demo profiles)
DEMO_PROFILES: dict[str, dict] = {
    "High-Energy Pop": {
        "favorite_genres": {"pop": 1.0, "indie pop": 0.7, "house": 0.5},
        "favorite_moods": {"happy": 1.0, "festive": 0.7},
        "target_energy": 0.86,
        "target_tempo_bpm": 126,
        "target_valence": 0.82,
        "target_danceability": 0.88,
        "target_acousticness": 0.15,
    },
    "Chill Lofi": {
        "favorite_genres": {"lofi": 1.0, "ambient": 0.8, "jazz": 0.4},
        "favorite_moods": {"chill": 1.0, "focused": 0.8, "relaxed": 0.6},
        "target_energy": 0.38,
        "target_tempo_bpm": 76,
        "target_valence": 0.60,
        "target_danceability": 0.56,
        "target_acousticness": 0.82,
    },
    "Deep Intense Rock": {
        "favorite_genres": {"rock": 1.0, "metal": 0.8},
        "favorite_moods": {"intense": 1.0, "aggressive": 0.8, "moody": 0.4},
        "target_energy": 0.93,
        "target_tempo_bpm": 154,
        "target_valence": 0.45,
        "target_danceability": 0.58,
        "target_acousticness": 0.08,
    },
    "Acoustic Relaxed": {
        "favorite_genres": {"folk": 1.0, "classical": 0.7, "jazz": 0.6},
        "favorite_moods": {"relaxed": 1.0, "serene": 0.8, "tender": 0.7},
        "target_energy": 0.32,
        "target_tempo_bpm": 78,
        "target_valence": 0.66,
        "target_danceability": 0.42,
        "target_acousticness": 0.90,
    },
    "Night Drive Moody": {
        "favorite_genres": {"synthwave": 1.0, "house": 0.6, "rock": 0.3},
        "favorite_moods": {"moody": 1.0, "focused": 0.5, "confident": 0.4},
        "target_energy": 0.74,
        "target_tempo_bpm": 112,
        "target_valence": 0.50,
        "target_danceability": 0.74,
        "target_acousticness": 0.20,
    },
}


# Helpers
def _print_top_k(
    title: str,
    recommendations: List[Tuple[dict, float, str]],
    output_fn: Callable[[str], None] = print,
) -> None:
    output_fn(f"\n=== {title} ===\n")
    output_fn(f"{'Rank':<6}{'ID':<5}{'Title':<24}{'Score':<8}Reasons")
    output_fn("-" * 95)
    for i, (song, score, reasons) in enumerate(recommendations, start=1):
        output_fn(
            f"{i:<6}{song['id']:<5}{song['title'][:22]:<24}{score:<8.2f}{reasons}"
        )


def _load_tuned_config(
    path: str = "evidence/tuned_config.json",
) -> Optional[ScoringConfig]:
    p = Path(path)
    if not p.exists():
        return None
    return ScoringConfig(**json.loads(p.read_text()))


def _ensure_tuned_config(path: str = "evidence/tuned_config.json") -> ScoringConfig:
    cfg = _load_tuned_config(path)
    if cfg is not None:
        return cfg
    # Lazy-import to avoid forcing agent dependencies in demo mode.
    print(f"(no tuned config at {path}; running agent to produce one)")
    from src.agent import WeightTuningAgent
    agent = WeightTuningAgent(seed=1, step_size=0.5, patience=15)
    history = agent.run(budget=30)
    final = ScoringConfig()
    for s in history:
        if s.accepted:
            final = s.after
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(final.to_dict(), indent=2) + "\n")
    return final


# Demo mode (also reused by --tune)
def run_demo(config: Optional[ScoringConfig] = None) -> None:
    songs = load_songs("data/songs.csv")
    label = "tuned" if config is not None else "default"
    print(f"(scoring with {label} config)")
    for name, profile_dict in DEMO_PROFILES.items():
        user = UserProfile(**profile_dict)
        recs = recommend_songs(user, songs, k=5, config=config)
        _print_top_k(name, recs)


# Interactive mode
def _apply_action(
    profile: UserProfile,
    action,
) -> UserProfile:
    """Return a new UserProfile with the action applied. Pure (no side effects)."""
    new_profile = deepcopy(profile)
    if isinstance(action, LikeSong):
        if action.song_id not in new_profile.liked_song_ids:
            new_profile.liked_song_ids = [*new_profile.liked_song_ids, action.song_id]
        # remove from disliked if present so the change is meaningful
        if action.song_id in new_profile.disliked_song_ids:
            new_profile.disliked_song_ids = [
                s for s in new_profile.disliked_song_ids if s != action.song_id
            ]
    elif isinstance(action, DislikeSong):
        if action.song_id not in new_profile.disliked_song_ids:
            new_profile.disliked_song_ids = [*new_profile.disliked_song_ids, action.song_id]
        if action.song_id in new_profile.liked_song_ids:
            new_profile.liked_song_ids = [
                s for s in new_profile.liked_song_ids if s != action.song_id
            ]
    elif isinstance(action, AdjustTarget):
        current = getattr(new_profile, action.field)
        if current is None:
            current = 0.5 if action.field != "target_tempo_bpm" else 100.0
        new_value = current + action.delta
        # clamp to safe ranges so validate() doesn't reject the proposal
        if action.field == "target_tempo_bpm":
            new_value = max(40.0, min(220.0, new_value))
        else:
            new_value = max(0.0, min(1.0, new_value))
        setattr(new_profile, action.field, new_value)
    return new_profile


def _semantic_check(
    before: UserProfile,
    after: UserProfile,
    action,
    songs_in_catalog: List[dict],
    config: Optional[ScoringConfig],
) -> Tuple[bool, str]:
    """
    Confirm the change actually had the intended effect on the relevant song.

    For Like:    the song's score must rise (or stay equal if already liked).
    For Dislike: the song's score must fall.
    For Adjust:  no per-song check; rely on validate() for safety.
    """
    if isinstance(action, (LikeSong, DislikeSong)):
        sid = action.song_id
        match = next((s for s in songs_in_catalog if s["id"] == sid), None)
        if match is None:
            return False, f"song id {sid} not found in catalog"
        song_obj = Song(**match)
        score_before, _ = score_song(before, song_obj, config)
        score_after, _ = score_song(after, song_obj, config)
        if isinstance(action, LikeSong) and score_after < score_before:
            return False, (
                f"like did not raise the score: "
                f"{score_before:.2f} -> {score_after:.2f}"
            )
        if isinstance(action, DislikeSong) and score_after > score_before:
            return False, (
                f"dislike did not lower the score: "
                f"{score_before:.2f} -> {score_after:.2f}"
            )
    return True, "ok"


def run_interactive(
    starting_profile_name: str = "High-Energy Pop",
    config: Optional[ScoringConfig] = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    log_path: str = "logs/agent.jsonl",
) -> UserProfile:
    """
    Interactive feedback loop. Returns the final UserProfile.

    All proposals go through:
        parse -> apply -> validate (raises -> rollback)
              -> semantic check  (fails -> rollback)
              -> log + commit
    """
    songs = load_songs("data/songs.csv")
    if starting_profile_name not in DEMO_PROFILES:
        raise ValueError(f"unknown profile {starting_profile_name!r}")

    profile = UserProfile(**DEMO_PROFILES[starting_profile_name])
    logger = get_logger(f"interactive::{log_path}", log_path=log_path)
    log_event(
        logger,
        "interactive_start",
        starting_profile=starting_profile_name,
    )

    output_fn(
        "\nInteractive mode. Commands: like <id>, dislike <id>, "
        "more <field>, less <field>, done\n"
        "Adjustable fields: energy, valence, danceability, acoustic, tempo\n"
    )

    while True:
        recs = recommend_songs(profile, songs, k=5, config=config)
        _print_top_k(f"{starting_profile_name} (current)", recs, output_fn=output_fn)

        try:
            raw = input_fn("\nfeedback? ")
        except EOFError:
            output_fn("\n(end of input)")
            break

        action = parse_feedback(raw)

        if isinstance(action, Done):
            output_fn("done.")
            log_event(logger, "interactive_done")
            break

        if isinstance(action, Unknown):
            output_fn(f"  ! unrecognized: {action.raw!r}. {action.hint or ''}")
            log_event(logger, "interactive_rejected", raw=action.raw, reason="parse_unknown")
            continue

        candidate = _apply_action(profile, action)

        # Layer 1: hard validation
        try:
            candidate.validate()
        except ValueError as exc:
            output_fn(f"  ! rejected by validator: {exc}")
            log_event(
                logger,
                "interactive_rejected",
                action=action.__class__.__name__,
                reason=f"validation_error: {exc}",
            )
            continue

        # Layer 2: semantic check (did the change do what was asked?)
        ok, reason = _semantic_check(profile, candidate, action, songs, config)
        if not ok:
            output_fn(f"  ! rejected by semantic check: {reason}")
            log_event(
                logger,
                "interactive_rejected",
                action=action.__class__.__name__,
                reason=reason,
            )
            continue

        # Accept
        profile = candidate
        output_fn(f"  + accepted: {action.__class__.__name__}")
        log_event(
            logger,
            "interactive_accepted",
            action=action.__class__.__name__,
            details=action.__dict__,
        )

    return profile


# CLI dispatcher
def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Music recommender CLI.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--tune", action="store_true", help="run demo using tuned ScoringConfig")
    mode.add_argument("--interactive", action="store_true", help="run interactive feedback loop")
    parser.add_argument("--profile", default="High-Energy Pop", help="starting profile for --interactive")
    parser.add_argument("--tuned-config", default="evidence/tuned_config.json")
    args = parser.parse_args(argv)

    config: Optional[ScoringConfig] = None
    if args.tune or args.interactive:
        # both modes can benefit from the tuned config; --interactive uses it if present
        config = _load_tuned_config(args.tuned_config)

    if args.tune:
        if config is None:
            config = _ensure_tuned_config(args.tuned_config)
        run_demo(config=config)
        return 0

    if args.interactive:
        run_interactive(
            starting_profile_name=args.profile,
            config=config,
        )
        return 0

    run_demo()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

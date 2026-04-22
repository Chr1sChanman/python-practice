"""
Free-form feedback parser for the interactive mode.

Maps short user commands to typed FeedbackAction objects:

    like 3              -> LikeSong(song_id=3)
    dislike 5           -> DislikeSong(song_id=5)
    more energy         -> AdjustTarget(field='target_energy', delta=+0.10)
    less acoustic       -> AdjustTarget(field='target_acousticness', delta=-0.10)
    done | quit | exit  -> Done()

Anything else returns Unknown(raw=...).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union


# Aliases users can type -> canonical UserProfile field name.
ADJUSTABLE_FIELDS = {
    "energy": "target_energy",
    "valence": "target_valence",
    "danceability": "target_danceability",
    "dance": "target_danceability",
    "acoustic": "target_acousticness",
    "acousticness": "target_acousticness",
    "tempo": "target_tempo_bpm",
}

ADJUST_DELTA_01 = 0.10        # for [0,1] bounded fields
ADJUST_DELTA_BPM = 5.0         # for tempo


@dataclass
class LikeSong:
    song_id: int


@dataclass
class DislikeSong:
    song_id: int


@dataclass
class AdjustTarget:
    field: str
    delta: float


@dataclass
class Done:
    pass


@dataclass
class Unknown:
    raw: str
    hint: Optional[str] = None


FeedbackAction = Union[LikeSong, DislikeSong, AdjustTarget, Done, Unknown]


def parse_feedback(text: str) -> FeedbackAction:
    """Parse one line of user feedback into a typed action."""
    raw = (text or "").strip().lower()
    if not raw:
        return Unknown(raw="", hint="empty input")

    if raw in {"done", "quit", "exit", "q"}:
        return Done()

    parts = raw.split()
    head = parts[0]

    if head in {"like", "dislike"} and len(parts) == 2:
        try:
            sid = int(parts[1])
        except ValueError:
            return Unknown(raw=raw, hint=f"expected an integer song id, got {parts[1]!r}")
        return LikeSong(song_id=sid) if head == "like" else DislikeSong(song_id=sid)

    if head in {"more", "less"} and len(parts) == 2:
        sign = +1.0 if head == "more" else -1.0
        alias = parts[1]
        if alias not in ADJUSTABLE_FIELDS:
            return Unknown(
                raw=raw,
                hint=f"unknown adjustable field {alias!r}; "
                     f"try one of {sorted(set(ADJUSTABLE_FIELDS.values()))}",
            )
        field = ADJUSTABLE_FIELDS[alias]
        delta = sign * (ADJUST_DELTA_BPM if field == "target_tempo_bpm" else ADJUST_DELTA_01)
        return AdjustTarget(field=field, delta=delta)

    return Unknown(
        raw=raw,
        hint='try: "like <id>", "dislike <id>", "more <field>", "less <field>", or "done"',
    )

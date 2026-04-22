from dataclasses import dataclass, asdict


@dataclass
class ScoringConfig:
    """
    All scoring weights in one place so they can be passed, logged, and compared.

    Defaults match the original hardcoded constants in score_song so existing
    callers that omit config= get identical behaviour.
    """
    w_genre: float = 1.25
    w_mood: float = 2.0
    w_energy: float = 4.0
    w_tempo: float = 1.2
    w_valence: float = 1.0
    w_dance: float = 1.0
    w_acoustic: float = 1.0
    w_artist: float = 1.0
    w_liked: float = 3.0
    w_disliked: float = -4.0

    def to_dict(self) -> dict:
        return asdict(self)

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import csv
import hashlib
import json
import time
import warnings

from src.config import ScoringConfig
from src.logging_utils import get_logger, log_event

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    # User's implicit preferences
    favorite_genres: dict[str, float] = field(default_factory=dict) # {"lofi": 1.0, "ambient": 0.7}
    favorite_moods: dict[str, float] = field(default_factory=dict)  # {"chill": 1.0, "focused": 0.8}

    # Target audio profile
    target_energy: float = 0.5
    target_tempo_bpm: float | None = None
    target_valence: float | None = None
    target_danceability: float | None = None
    target_acousticness: float | None = None

    # Interaction history
    liked_song_ids: list[int] = field(default_factory=list)
    disliked_song_ids: list[int] = field(default_factory=list)

    # Optional ranking ctrls
    artist_affinity: dict[str, float] = field(default_factory=dict)   # {"LoRoom": 0.6}
    novelty_preference: float = 0.25   # 0=very safe, 1=very exploratory
    diversity_preference: float = 0.20 # penalize too-similar top-k

    def validate(self) -> List[str]:
        """
        Validate the profile against runtime invariants.

        Behaviour split:
        - Hard violations raise ``ValueError`` (out-of-range numbers, negative
          weights). The system cannot reasonably interpret these.
        - Soft contradictions (e.g. same id liked AND disliked) emit a
          ``UserWarning`` and are returned in the warnings list, so callers
          (and logs) can surface them without halting.

        Returns:
            List of warning messages (empty if profile is clean).
        """
        warns: List[str] = []

        # 0-1 bounded fields
        bounded_01 = {
            "target_energy": self.target_energy,
            "target_valence": self.target_valence,
            "target_danceability": self.target_danceability,
            "target_acousticness": self.target_acousticness,
            "novelty_preference": self.novelty_preference,
            "diversity_preference": self.diversity_preference,
        }
        for name, value in bounded_01.items():
            if value is None:
                continue
            if not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"{name}={value!r} out of range; expected float in [0.0, 1.0]"
                )

        # tempo: positive BPM or None
        if self.target_tempo_bpm is not None and self.target_tempo_bpm <= 0:
            raise ValueError(
                f"target_tempo_bpm={self.target_tempo_bpm!r} must be > 0"
            )

        # weights in preference dicts must be non-negative
        for dict_name, d in (
            ("favorite_genres", self.favorite_genres),
            ("favorite_moods", self.favorite_moods),
            ("artist_affinity", self.artist_affinity),
        ):
            for key, weight in d.items():
                if weight < 0:
                    raise ValueError(
                        f"{dict_name}[{key!r}]={weight!r} must be >= 0"
                    )

        # soft contradiction: id appears in both liked and disliked
        overlap = set(self.liked_song_ids) & set(self.disliked_song_ids)
        if overlap:
            msg = (
                f"song id(s) {sorted(overlap)} appear in both liked_song_ids "
                f"and disliked_song_ids; like/dislike will partially cancel"
            )
            warns.append(msg)
            warnings.warn(msg, UserWarning, stacklevel=2)

        return warns


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Load and validate song rows from a CSV file.

    Args:
        csv_path: Relative or absolute path to the songs CSV.

    Returns:
        A list of song dictionaries with normalized value types:
        `id` as int, audio features as float, and text fields stripped.

    Raises:
        ValueError: If a required field is missing or a value cannot be cast
        to the expected type.
    """
    songs: List[Dict] = []

    with open(csv_path, mode="r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for line_num, row in enumerate(reader, start=2):  # header is line 1
            try:
                song = {
                    "id": int(row["id"]),
                    "title": row["title"].strip(),
                    "artist": row["artist"].strip(),
                    "genre": row["genre"].strip(),
                    "mood": row["mood"].strip(),
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            except (KeyError, ValueError) as e:
                raise ValueError(f"Invalid row at line {line_num}: {row}") from e

            songs.append(song)

    return songs

def _sim_01(a: float, b: float) -> float:
    """
    Compute bounded similarity for two values already on a 0-1 scale.

    Args:
        a: First normalized value.
        b: Second normalized value.

    Returns:
        Similarity in [0.0, 1.0], where 1.0 is identical and 0.0 is maximally
        distant under absolute-difference distance.
    """
    return max(0.0, 1.0 - abs(a - b))

def score_song(
    user: UserProfile,
    song: Song,
    config: Optional[ScoringConfig] = None,
) -> Tuple[float, str]:
    """
    Score one song against the user's taste profile.

    The score combines weighted genre/mood preferences, audio-feature
    similarity, interaction history boosts/penalties, and artist affinity.

    Args:
        user: Profile containing weighted preferences and optional targets.
        song: Candidate song to evaluate.
        config: Scoring weights. Defaults to ScoringConfig() if not provided.

    Returns:
        A tuple of:
        - final numeric score (higher is better)
        - short explanation string with top scoring reasons
    """
    if config is None:
        config = ScoringConfig()

    score = 0.0
    reasons: List[str] = []

    genre_pref = user.favorite_genres.get(song.genre, 0.0)
    if genre_pref > 0:
        pts = config.w_genre * genre_pref
        score += pts
        reasons.append(f"+{pts:.2f} genre:{song.genre}")

    mood_pref = user.favorite_moods.get(song.mood, 0.0)
    if mood_pref > 0:
        pts = config.w_mood * mood_pref
        score += pts
        reasons.append(f"+{pts:.2f} mood:{song.mood}")

    # Target audio profile similarity.
    energy_sim = _sim_01(song.energy, user.target_energy)
    pts = config.w_energy * energy_sim
    score += pts
    reasons.append(f"+{pts:.2f} energy similarity")

    if user.target_tempo_bpm is not None:
        tempo_sim = max(0.0, 1.0 - abs(song.tempo_bpm - user.target_tempo_bpm) / 90.0)
        pts = config.w_tempo * tempo_sim
        score += pts
        reasons.append(f"+{pts:.2f} tempo similarity")

    if user.target_valence is not None:
        pts = config.w_valence * _sim_01(song.valence, user.target_valence)
        score += pts
        reasons.append(f"+{pts:.2f} valence similarity")

    if user.target_danceability is not None:
        pts = config.w_dance * _sim_01(song.danceability, user.target_danceability)
        score += pts
        reasons.append(f"+{pts:.2f} danceability similarity")

    if user.target_acousticness is not None:
        pts = config.w_acoustic * _sim_01(song.acousticness, user.target_acousticness)
        score += pts
        reasons.append(f"+{pts:.2f} acousticness similarity")

    # Interaction history.
    if song.id in user.liked_song_ids:
        score += config.w_liked
        reasons.append(f"+{config.w_liked:.2f} previously liked")
    if song.id in user.disliked_song_ids:
        score += config.w_disliked
        reasons.append(f"{config.w_disliked:.2f} previously disliked")

    # Artist affinity.
    artist_pref = user.artist_affinity.get(song.artist, 0.0)
    if artist_pref > 0:
        pts = config.w_artist * artist_pref
        score += pts
        reasons.append(f"+{pts:.2f} artist:{song.artist}")

    explanation = "; ".join(reasons[:4]) if reasons else "No strong preference match"
    return score, explanation

def score_songs(
    user: UserProfile,
    songs: List[Song],
    config: Optional[ScoringConfig] = None,
) -> List[Tuple[Song, float, str]]:
    """
    Score every song candidate for a given user profile.

    Args:
        user: Profile used for scoring.
        songs: List of Song objects to evaluate.
        config: Scoring weights. Defaults to ScoringConfig() if not provided.

    Returns:
        List of `(song, score, explanation)` tuples in input order.
    """
    scored: List[Tuple[Song, float, str]] = []
    for song in songs:
        score, explanation = score_song(user, song, config)
        scored.append((song, score, explanation))
    return scored

def _profile_hash(user: UserProfile) -> str:
    """Stable short hash of a profile for log correlation."""
    payload = json.dumps(
        {
            "favorite_genres": user.favorite_genres,
            "favorite_moods": user.favorite_moods,
            "target_energy": user.target_energy,
            "target_tempo_bpm": user.target_tempo_bpm,
            "target_valence": user.target_valence,
            "target_danceability": user.target_danceability,
            "target_acousticness": user.target_acousticness,
            "liked_song_ids": sorted(user.liked_song_ids),
            "disliked_song_ids": sorted(user.disliked_song_ids),
            "artist_affinity": user.artist_affinity,
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:10]


def recommend_songs(
    user: UserProfile,
    songs: List[Dict],
    k: int = 5,
    config: Optional[ScoringConfig] = None,
) -> List[Tuple[Dict, float, str]]:
    """
    Return top-k recommendations as ranked song dictionaries.

    Validates ``user`` first (raises on hard violations, warns on soft ones)
    and emits one structured JSONL log line per call to
    ``logs/recommender.jsonl`` capturing inputs, top results, and latency.

    Args:
        user: User profile used for scoring.
        songs: Raw song dictionaries (typically from `load_songs`).
        k: Number of top recommendations to return.
        config: Scoring weights. Defaults to ScoringConfig() if not provided.

    Returns:
        Ranked list of `(song_dict, score, explanation)` tuples sorted by
        score descending.
    """
    logger = get_logger("recommender")
    profile_hash = _profile_hash(user)
    started = time.perf_counter()

    try:
        warns = user.validate()
    except ValueError as exc:
        log_event(
            logger,
            "recommend_failed",
            profile_hash=profile_hash,
            k=k,
            error=str(exc),
            error_type=type(exc).__name__,
        )
        raise

    song_objs = [Song(**s) for s in songs]
    scored = score_songs(user, song_objs, config)
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)[:k]

    results = [
        (
            {
                "id": s.id,
                "title": s.title,
                "artist": s.artist,
                "genre": s.genre,
                "mood": s.mood,
                "energy": s.energy,
                "tempo_bpm": s.tempo_bpm,
                "valence": s.valence,
                "danceability": s.danceability,
                "acousticness": s.acousticness,
            },
            score,
            explanation,
        )
        for s, score, explanation in ranked
    ]

    latency_ms = (time.perf_counter() - started) * 1000.0
    log_event(
        logger,
        "recommend",
        profile_hash=profile_hash,
        k=k,
        catalog_size=len(songs),
        top_ids=[song["id"] for song, _, _ in results],
        top_scores=[round(score, 4) for _, score, _ in results],
        warnings=warns,
        latency_ms=round(latency_ms, 3),
    )
    return results

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import csv

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
    Loads songs from a CSV file.
    Required by src/main.py
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
    return max(0.0, 1.0 - abs(a - b))

def score_song(user: UserProfile, song: Song) -> Tuple[float, str]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons: List[str] = []

    # Weights
    W_GENRE = 2.5
    W_MOOD = 2.0
    W_ENERGY = 2.0
    W_TEMPO = 1.2
    W_VALENCE = 1.0
    W_DANCE = 1.0
    W_ACOUSTIC = 1.0
    W_ARTIST = 1.0
    W_LIKED = 3.0
    W_DISLIKED = -4.0

    genre_pref = user.favorite_genres.get(song.genre, 0.0)
    if genre_pref > 0:
        pts = W_GENRE * genre_pref
        score += pts
        reasons.append(f"+{pts:.2f} genre:{song.genre}")

    mood_pref = user.favorite_moods.get(song.mood, 0.0)
    if mood_pref > 0:
        pts = W_MOOD * mood_pref
        score += pts
        reasons.append(f"+{pts:.2f} mood:{song.mood}")

    # 2) Target audio profile similarity
    energy_sim = _sim_01(song.energy, user.target_energy)
    pts = W_ENERGY * energy_sim
    score += pts
    reasons.append(f"+{pts:.2f} energy similarity")

    if user.target_tempo_bpm is not None:
        tempo_sim = max(0.0, 1.0 - abs(song.tempo_bpm - user.target_tempo_bpm) / 90.0)
        pts = W_TEMPO * tempo_sim
        score += pts
        reasons.append(f"+{pts:.2f} tempo similarity")

    if user.target_valence is not None:
        pts = W_VALENCE * _sim_01(song.valence, user.target_valence)
        score += pts
        reasons.append(f"+{pts:.2f} valence similarity")

    if user.target_danceability is not None:
        pts = W_DANCE * _sim_01(song.danceability, user.target_danceability)
        score += pts
        reasons.append(f"+{pts:.2f} danceability similarity")

    if user.target_acousticness is not None:
        pts = W_ACOUSTIC * _sim_01(song.acousticness, user.target_acousticness)
        score += pts
        reasons.append(f"+{pts:.2f} acousticness similarity")

    # 3) Interaction history
    if song.id in user.liked_song_ids:
        score += W_LIKED
        reasons.append(f"+{W_LIKED:.2f} previously liked")
    if song.id in user.disliked_song_ids:
        score += W_DISLIKED
        reasons.append(f"{W_DISLIKED:.2f} previously disliked")

    # 4) Artist affinity
    artist_pref = user.artist_affinity.get(song.artist, 0.0)
    if artist_pref > 0:
        pts = W_ARTIST * artist_pref
        score += pts
        reasons.append(f"+{pts:.2f} artist:{song.artist}")

    explanation = "; ".join(reasons[:4]) if reasons else "No strong preference match"
    return score, explanation

def score_songs(user: UserProfile, songs: List[Song]) -> List[Tuple[Song, float, str]]:
    scored: List[Tuple[Song, float, str]] = []
    for song in songs:
        score, explanation = score_song(user, song)
        scored.append((song, score, explanation))
    return scored

def recommend_songs(user: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    song_objs = [Song(**s) for s in songs]
    scored = score_songs(user, song_objs)
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)[:k]

    return [
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


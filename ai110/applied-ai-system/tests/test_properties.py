"""
Phase 4 tests: property-based invariants via hypothesis.

Each test expresses a rule that must hold for *every* valid input, not just
the handful of cases a unit test happens to cover. When a property fails,
hypothesis will shrink the failing example to the simplest possible case.
"""
from copy import deepcopy

from hypothesis import given, settings
from hypothesis import strategies as st

from src.config import ScoringConfig
from src.recommender import Song, UserProfile, score_song


# Strategies for random-but-valid domain objects
GENRES = st.sampled_from(["pop", "lofi", "rock", "jazz", "synthwave", "ambient"])
MOODS = st.sampled_from(["happy", "chill", "intense", "moody", "relaxed", "focused"])


@st.composite
def songs(draw):
    return Song(
        id=draw(st.integers(min_value=1, max_value=1000)),
        title="t",
        artist=draw(st.sampled_from(["ArtistA", "ArtistB", "ArtistC"])),
        genre=draw(GENRES),
        mood=draw(MOODS),
        energy=draw(st.floats(min_value=0.0, max_value=1.0)),
        tempo_bpm=draw(st.floats(min_value=40.0, max_value=200.0)),
        valence=draw(st.floats(min_value=0.0, max_value=1.0)),
        danceability=draw(st.floats(min_value=0.0, max_value=1.0)),
        acousticness=draw(st.floats(min_value=0.0, max_value=1.0)),
    )


@st.composite
def profiles(draw):
    return UserProfile(
        favorite_genres={
            draw(GENRES): draw(st.floats(min_value=0.0, max_value=1.0)),
        },
        favorite_moods={
            draw(MOODS): draw(st.floats(min_value=0.0, max_value=1.0)),
        },
        target_energy=draw(st.floats(min_value=0.0, max_value=1.0)),
        target_valence=draw(st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0))),
        target_danceability=draw(st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0))),
        target_acousticness=draw(st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0))),
    )


# Invariants 
@given(profile=profiles(), song=songs())
@settings(deadline=None, max_examples=100)
def test_determinism_same_inputs_same_output(profile, song):
    """score_song is pure: same (profile, song, config) -> same score."""
    config = ScoringConfig()
    s1, e1 = score_song(profile, song, config)
    s2, e2 = score_song(profile, song, config)
    assert s1 == s2
    assert e1 == e2


@given(profile=profiles(), song=songs())
@settings(deadline=None, max_examples=100)
def test_like_monotonicity_never_decreases_score(profile, song):
    """Adding a song id to liked_song_ids must not lower its score."""
    profile_without = deepcopy(profile)
    profile_without.liked_song_ids = []
    profile_with = deepcopy(profile_without)
    profile_with.liked_song_ids = [song.id]

    s_without, _ = score_song(profile_without, song)
    s_with, _ = score_song(profile_with, song)
    assert s_with >= s_without, (
        f"like lowered score: without={s_without}, with={s_with}"
    )


@given(profile=profiles(), song=songs())
@settings(deadline=None, max_examples=100)
def test_dislike_monotonicity_never_increases_score(profile, song):
    """Adding a song id to disliked_song_ids must not raise its score."""
    profile_without = deepcopy(profile)
    profile_without.disliked_song_ids = []
    profile_with = deepcopy(profile_without)
    profile_with.disliked_song_ids = [song.id]

    s_without, _ = score_song(profile_without, song)
    s_with, _ = score_song(profile_with, song)
    assert s_with <= s_without, (
        f"dislike raised score: without={s_without}, with={s_with}"
    )


@given(
    profile=profiles(),
    song=songs(),
    bump=st.floats(min_value=0.01, max_value=2.0),
)
@settings(deadline=None, max_examples=100)
def test_genre_weight_monotonicity(profile, song, bump):
    """Raising favorite_genres[song.genre] never decreases the song's score."""
    base = deepcopy(profile)
    higher = deepcopy(profile)
    current = higher.favorite_genres.get(song.genre, 0.0)
    higher.favorite_genres = dict(higher.favorite_genres)
    higher.favorite_genres[song.genre] = current + bump

    s_base, _ = score_song(base, song)
    s_higher, _ = score_song(higher, song)
    assert s_higher >= s_base, (
        f"raising genre weight lowered score: base={s_base}, higher={s_higher}"
    )

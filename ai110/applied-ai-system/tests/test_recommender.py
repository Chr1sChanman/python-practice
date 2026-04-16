from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    load_songs,
    recommend_songs,
    score_song,
    score_songs,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genres={"pop": 1.0},
        favorite_moods={"happy": 1.0},
        target_energy=0.8,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genres={"pop": 1.0},
        favorite_moods={"happy": 1.0},
        target_energy=0.8,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_score_song_prefers_weighted_genre_mood_and_energy_match():
    songs = make_small_recommender().songs
    pop_song = songs[0]
    lofi_song = songs[1]

    user = UserProfile(
        favorite_genres={"pop": 1.0, "lofi": 0.2},
        favorite_moods={"happy": 1.0, "chill": 0.3},
        target_energy=0.8,
    )

    pop_score, pop_explanation = score_song(user, pop_song)
    lofi_score, _ = score_song(user, lofi_song)

    assert pop_score > lofi_score
    assert "genre:pop" in pop_explanation
    assert "mood:happy" in pop_explanation


def test_score_song_penalizes_disliked_and_boosts_liked():
    songs = make_small_recommender().songs
    pop_song = songs[0]
    lofi_song = songs[1]

    user = UserProfile(
        favorite_genres={"pop": 1.0, "lofi": 1.0},
        favorite_moods={"happy": 1.0, "chill": 1.0},
        target_energy=0.6,
        liked_song_ids=[2],
        disliked_song_ids=[1],
    )

    pop_score, _ = score_song(user, pop_song)
    lofi_score, _ = score_song(user, lofi_song)
    assert lofi_score > pop_score


def test_score_songs_returns_tuple_per_input_song():
    songs = make_small_recommender().songs
    user = UserProfile(target_energy=0.5)

    scored = score_songs(user, songs)
    assert len(scored) == len(songs)
    assert all(len(item) == 3 for item in scored)
    assert all(isinstance(item[1], float) for item in scored)


def test_edge_profile_weight_inflation_can_override_audio_mismatch():
    songs = load_songs("data/songs.csv")
    edge_user = UserProfile(
        favorite_genres={"pop": 100.0, "indie pop": 80.0},
        favorite_moods={"happy": 100.0},
        target_energy=0.10,
        target_tempo_bpm=60,
        target_valence=0.10,
        target_danceability=0.10,
        target_acousticness=0.95,
        liked_song_ids=[],
        disliked_song_ids=[],
        artist_affinity={},
        novelty_preference=0.0,
        diversity_preference=0.0,
    )

    ranked = recommend_songs(edge_user, songs, k=3)
    top_song = ranked[0][0]

    # With inflated preference weights, pop/happy should still dominate even
    # when audio targets are intentionally opposite.
    assert top_song["genre"] == "pop"
    assert top_song["mood"] == "happy"


def test_edge_profile_conflicting_like_dislike_has_net_negative_effect():
    song = make_small_recommender().songs[0]
    baseline_user = UserProfile(
        favorite_genres={"pop": 1.0},
        favorite_moods={"happy": 1.0},
        target_energy=0.8,
        target_tempo_bpm=120,
        target_valence=0.8,
        target_danceability=0.8,
        target_acousticness=0.2,
        liked_song_ids=[],
        disliked_song_ids=[],
        artist_affinity={"Test Artist": 0.5},
        novelty_preference=0.5,
        diversity_preference=0.5,
    )

    conflict_user = UserProfile(
        favorite_genres={"pop": 1.0},
        favorite_moods={"happy": 1.0},
        target_energy=0.8,
        target_tempo_bpm=120,
        target_valence=0.8,
        target_danceability=0.8,
        target_acousticness=0.2,
        liked_song_ids=[song.id],
        disliked_song_ids=[song.id],
        artist_affinity={"Test Artist": 0.5},
        novelty_preference=0.5,
        diversity_preference=0.5,
    )

    baseline_score, _ = score_song(baseline_user, song)
    conflict_score, _ = score_song(conflict_user, song)

    # Current logic applies both adjustments (+3 and -4), yielding net -1.
    assert conflict_score == baseline_score - 1.0

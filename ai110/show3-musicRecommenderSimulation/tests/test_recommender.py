from src.recommender import Song, UserProfile, Recommender, score_song, score_songs

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

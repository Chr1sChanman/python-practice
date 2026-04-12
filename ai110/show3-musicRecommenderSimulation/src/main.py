"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs, UserProfile

def main() -> None:
    """
    Run demo recommendations for multiple distinct taste profiles.

    Loads the CSV catalog, defines five named user preference dictionaries,
    converts each dictionary to a `UserProfile`, and prints top-k ranked
    recommendations with score explanations.
    """
    songs = load_songs("data/songs.csv")

    user_preference_profiles = {
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

    for profile_name, profile_dict in user_preference_profiles.items():
        user = UserProfile(**profile_dict)
        recommendations = recommend_songs(user, songs, k=5)

        print(f"\n=== {profile_name} ===\n")
        print(f"{'Rank':<6}{'Title':<24}{'Score':<8}Reasons")
        print("-" * 90)
        for i, (song, score, reasons) in enumerate(recommendations, start=1):
            print(f"{i:<6}{song['title'][:22]:<24}{score:<8.2f}{reasons}")



if __name__ == "__main__":
    main()

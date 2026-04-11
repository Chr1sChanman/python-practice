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
    songs = load_songs("data/songs.csv")

    user = UserProfile(
        favorite_genres={"pop": 1.0, "indie pop": 0.7},
        favorite_moods={"happy": 1.0},
        target_energy=0.8,
        target_tempo_bpm=120,
        target_valence=0.8,
        target_danceability=0.8,
        target_acousticness=0.25,
    )

    recommendations = recommend_songs(user, songs, k=5)

    print("\nTop Recommendations\n")
    print(f"{'Rank':<6}{'Title':<24}{'Score':<8}Reasons")
    print("-" * 90)
    for i, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"{i:<6}{song['title'][:22]:<24}{score:<8.2f}{reasons}")



if __name__ == "__main__":
    main()

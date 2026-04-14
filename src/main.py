"""
Command line runner for the Music Recommender Simulation.

Three contrasting taste profiles demonstrate that the scoring formula
surfaces completely different results for completely different listeners.
"""

try:
    from src.recommender import load_songs, recommend_songs   # python -m src.main
except ModuleNotFoundError:
    from recommender import load_songs, recommend_songs       # python src/main.py


# ---------------------------------------------------------------------------
# Taste profiles
# ---------------------------------------------------------------------------

# Default profile — verifies the system surfaces the expected pop/happy songs
POP_LISTENER = {
    "genre":        "pop",
    "mood":         "happy",
    "energy":       0.80,
    "valence":      0.80,
    "acousticness": 0.20,
    "tempo_bpm":    120,
    "danceability": 0.80,
}

# Profile B — high-energy rock listener
ROCK_LISTENER = {
    "genre":        "rock",
    "mood":         "intense",
    "energy":       0.88,
    "valence":      0.45,
    "acousticness": 0.10,
    "tempo_bpm":    140,
    "danceability": 0.62,
}

# Profile C — low-energy lofi listener (opposite end of the feature space)
LOFI_LISTENER = {
    "genre":        "lofi",
    "mood":         "chill",
    "energy":       0.38,
    "valence":      0.60,
    "acousticness": 0.82,
    "tempo_bpm":    76,
    "danceability": 0.55,
}


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

_BAR_WIDTH = 20


def _score_bar(score: float) -> str:
    """Return a filled/empty block bar scaled to _BAR_WIDTH characters."""
    filled = round(score * _BAR_WIDTH)
    return "\u2588" * filled + "\u2591" * (_BAR_WIDTH - filled)


def _strip_score_prefix(explanation: str) -> str:
    """Remove 'Score X.XX \u2014 ' prefix; score is already shown on its own line."""
    if " \u2014 " in explanation:
        return explanation.split(" \u2014 ", 1)[1].rstrip(".")
    return explanation.rstrip(".")


def run(label: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a formatted recommendation block for one taste profile."""
    width = 62
    divider      = "=" * width
    thin_divider = "\u2500" * width

    print(f"\n{divider}")
    print(f"  Profile : {label}")
    print(f"  Prefs   : genre={user_prefs['genre']}  "
          f"mood={user_prefs['mood']}  "
          f"energy={user_prefs['energy']}")
    print(divider)

    recommendations = recommend_songs(user_prefs, songs, k=k)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        if rank > 1:
            print(f"  {thin_divider}")

        reasons = _strip_score_prefix(explanation)

        print(f"\n  #{rank}  {song['title']}")
        print(f"        Score  : {score:.2f}  [{_score_bar(score)}]")
        print(f"        Artist : {song['artist']}  |  "
              f"{song['genre']} / {song['mood']}")
        print(f"        Why    : {reasons}")

    print(f"\n{divider}\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    run("Pop / Happy Listener",        POP_LISTENER,  songs)
    run("High-Energy Rock Listener",   ROCK_LISTENER, songs)
    run("Chill Lofi Listener",         LOFI_LISTENER, songs)


if __name__ == "__main__":
    main()

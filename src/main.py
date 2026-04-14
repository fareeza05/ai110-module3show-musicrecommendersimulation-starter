"""
Command line runner for the Music Recommender Simulation.

Section 1 — Standard profiles: three well-formed listener types that
            demonstrate the system working as intended.
Section 2 — Adversarial profiles: five edge-case profiles designed to
            expose failure modes, biases, and unexpected behaviours in
            the scoring logic.
"""

try:
    from src.recommender import load_songs, recommend_songs   # python -m src.main
except ModuleNotFoundError:
    from recommender import load_songs, recommend_songs       # python src/main.py


# ---------------------------------------------------------------------------
# Section 1 — Standard taste profiles
# ---------------------------------------------------------------------------

POP_LISTENER = {
    "genre":        "pop",
    "mood":         "happy",
    "energy":       0.80,
    "valence":      0.80,
    "acousticness": 0.20,
    "tempo_bpm":    120,
    "danceability": 0.80,
}

ROCK_LISTENER = {
    "genre":        "rock",
    "mood":         "intense",
    "energy":       0.88,
    "valence":      0.45,
    "acousticness": 0.10,
    "tempo_bpm":    140,
    "danceability": 0.62,
}

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
# Section 2 — Adversarial / edge-case profiles
# Each profile is designed to trigger a specific known weakness.
# ---------------------------------------------------------------------------

# Edge case 1 — Ghost Profile
# No genre or mood specified; every feature at neutral 0.5.
# Exposes the neutral default bias: the system must rank entirely on audio
# proximity to the midpoint, silently surfacing whatever sits closest to
# the centre of every feature dimension.
GHOST_PROFILE = {
    "energy":       0.50,
    "valence":      0.50,
    "acousticness": 0.50,
    "tempo_bpm":    106,    # midpoint of dataset range (60–152)
    "danceability": 0.50,
}

# Edge case 2 — Sad Banger
# High-energy metal listener who says their mood is "melancholic".
# No song in the catalog is both metal AND melancholic.
# Exposes the catalog gap problem and tests whether the genre weight (3.0)
# overrides the mood weight (2.0) when they point to different songs.
SAD_BANGER = {
    "genre":        "metal",
    "mood":         "melancholic",
    "energy":       0.92,
    "valence":      0.25,
    "acousticness": 0.05,
    "tempo_bpm":    148,
    "danceability": 0.50,
}

# Edge case 3 — Acoustic Rager
# Rock/intense listener who also wants highly acoustic production.
# In the dataset, rock and high acousticness are inversely correlated —
# Storm Runner has acousticness=0.10, the opposite of 0.90.
# Exposes the collinearity bias: the system must choose between a strong
# categorical double-match and a large numeric contradiction.
ACOUSTIC_RAGER = {
    "genre":        "rock",
    "mood":         "intense",
    "energy":       0.90,
    "valence":      0.45,
    "acousticness": 0.90,   # contradicts rock genre
    "tempo_bpm":    140,
    "danceability": 0.62,
}

# Edge case 4 — Catalog Gap
# Wants classical music but in an "angry" mood.
# No classical+angry song exists. Genre and mood signals point to
# completely different songs — Quiet Arpeggios (classical/peaceful) vs
# Iron Pulse (metal/angry).
# Tests which categorical weight wins when they cannot both be satisfied.
CATALOG_GAP = {
    "genre":        "classical",
    "mood":         "angry",
    "energy":       0.30,
    "valence":      0.25,
    "acousticness": 0.95,
    "tempo_bpm":    80,
    "danceability": 0.30,
}

# Edge case 5 — Energy Paradox
# Genuine lofi/chill listener who somehow wants EDM-level energy (0.95).
# All three lofi songs in the catalog have energy between 0.35 and 0.42 —
# far from the target.
# Exposes genre dominance bias: the categorical genre+mood match (5.0 pts)
# should still outweigh the large energy penalty, recommending quiet lofi
# songs to a user who said they want very high energy.
ENERGY_PARADOX = {
    "genre":        "lofi",
    "mood":         "chill",
    "energy":       0.95,   # impossible for any lofi song in catalog
    "valence":      0.60,
    "acousticness": 0.80,
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


def run(label: str, user_prefs: dict, songs: list, k: int = 5,
        note: str = "") -> None:
    """Print a formatted recommendation block for one taste profile."""
    width = 62
    divider      = "=" * width
    thin_divider = "\u2500" * width

    genre = user_prefs.get("genre", "(none)")
    mood  = user_prefs.get("mood",  "(none)")

    print(f"\n{divider}")
    print(f"  Profile : {label}")
    print(f"  Prefs   : genre={genre}  mood={mood}  energy={user_prefs.get('energy', 0.5)}")
    if note:
        print(f"  Note    : {note}")
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

    # --- Standard profiles ------------------------------------------------
    print("\n" + "#" * 62)
    print("  STANDARD PROFILES")
    print("#" * 62)

    run("Pop / Happy Listener",      POP_LISTENER,  songs)
    run("High-Energy Rock Listener", ROCK_LISTENER, songs)
    run("Chill Lofi Listener",       LOFI_LISTENER, songs)

    # --- Adversarial profiles ---------------------------------------------
    print("\n" + "#" * 62)
    print("  ADVERSARIAL / EDGE-CASE PROFILES")
    print("#" * 62)

    run(
        "Ghost Profile (no genre or mood)",
        GHOST_PROFILE, songs,
        note="All categoricals absent — pure audio proximity decides ranking",
    )
    run(
        "Sad Banger (metal + melancholic — catalog gap)",
        SAD_BANGER, songs,
        note="No metal/melancholic song exists; genre weight should beat mood weight",
    )
    run(
        "Acoustic Rager (rock/intense + acousticness=0.90)",
        ACOUSTIC_RAGER, songs,
        note="Contradictory numerics — Storm Runner has acousticness=0.10",
    )
    run(
        "Catalog Gap (classical + angry — impossible combo)",
        CATALOG_GAP, songs,
        note="Genre and mood point to different songs with zero overlap",
    )
    run(
        "Energy Paradox (lofi/chill + energy=0.95)",
        ENERGY_PARADOX, songs,
        note="Genre dominance should surface lofi songs despite huge energy mismatch",
    )


if __name__ == "__main__":
    main()

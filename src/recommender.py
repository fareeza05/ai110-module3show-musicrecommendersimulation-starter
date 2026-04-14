from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

# ---------------------------------------------------------------------------
# Feature weights — higher = more influence on the final score
#
# Rule: categorical hard-boundaries (genre, mood) outweigh numeric features
# because a genre mismatch is a recommendation failure, not just a miss.
# ---------------------------------------------------------------------------
WEIGHTS = {
    "genre":        3.0,   # hardest boundary — wrong genre = wrong listener
    "mood":         2.0,   # direct intent signal from the user
    "energy":       1.5,   # strongest numeric discriminator in the dataset
    "valence":      1.2,   # emotional tone, independent of energy
    "acousticness": 1.0,   # strong organic/electronic separator
    "tempo":        0.5,   # soft constraint — ±10 BPM is rarely a dealbreaker
    "danceability": 0.3,   # largely redundant with energy at this dataset size
}
TOTAL_WEIGHT = sum(WEIGHTS.values())   # 9.5

# Tempo normalization bounds (min/max BPM observed in songs.csv)
TEMPO_MIN, TEMPO_MAX = 60.0, 152.0


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

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
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Core scoring helpers
# ---------------------------------------------------------------------------

def _proximity(song_val: float, user_val: float) -> float:
    """Return 1 − |song_val − user_val|, rewarding closeness over raw magnitude."""
    return 1.0 - abs(song_val - user_val)


def _normalize_tempo(bpm: float) -> float:
    """Map BPM to [0, 1] using the dataset's observed range."""
    return (bpm - TEMPO_MIN) / (TEMPO_MAX - TEMPO_MIN)


# ---------------------------------------------------------------------------
# OOP scoring (Song + UserProfile dataclasses)
# ---------------------------------------------------------------------------

def _score_song_oop(song: Song, user: UserProfile) -> float:
    """Return a normalized weighted proximity score for a Song against a UserProfile."""
    # Convert likes_acoustic bool to a target acousticness value
    target_acousticness = 0.85 if user.likes_acoustic else 0.15

    weighted_sum = (
        WEIGHTS["genre"]        * (1.0 if song.genre == user.favorite_genre else 0.0)
      + WEIGHTS["mood"]         * (1.0 if song.mood  == user.favorite_mood  else 0.0)
      + WEIGHTS["energy"]       * _proximity(song.energy,       user.target_energy)
      + WEIGHTS["valence"]      * _proximity(song.valence,      0.5)                  # neutral default
      + WEIGHTS["acousticness"] * _proximity(song.acousticness, target_acousticness)
      + WEIGHTS["tempo"]        * _proximity(_normalize_tempo(song.tempo_bpm), 0.5)   # neutral default
      + WEIGHTS["danceability"] * _proximity(song.danceability, 0.5)                  # neutral default
    )
    return round(weighted_sum / TOTAL_WEIGHT, 4)


def score_song(user_prefs: Dict, song: Dict) -> float:
    """Score one song against user preferences using the 7-feature weighted proximity recipe."""
    # ------------------------------------------------------------------
    # Step 1 — Genre: hard categorical gate (weight 3.0)
    # A genre mismatch costs more than any single numeric feature can
    # recover, preventing the system from recommending a rock song to a
    # lofi listener just because their BPM and energy numbers align.
    # ------------------------------------------------------------------
    genre_score = 3.0 if song["genre"] == user_prefs.get("genre", "") else 0.0

    # ------------------------------------------------------------------
    # Step 2 — Mood: session intent signal (weight 2.0)
    # Mood reflects what the listener wants right now, not just their
    # long-term taste, so it outweighs every individual audio feature.
    # ------------------------------------------------------------------
    mood_score = 2.0 if song["mood"] == user_prefs.get("mood", "") else 0.0

    # ------------------------------------------------------------------
    # Steps 3–7 — Numeric features: proximity scoring
    # Formula: 1 − |song_value − user_preference|
    # Returns 1.0 for identical values, 0.0 for maximum difference.
    # Rewards closeness to preference rather than raw magnitude.
    # ------------------------------------------------------------------
    energy_score       = 1.5 * _proximity(float(song["energy"]),
                                           float(user_prefs.get("energy",       0.5)))

    valence_score      = 1.2 * _proximity(float(song["valence"]),
                                           float(user_prefs.get("valence",      0.5)))

    acousticness_score = 1.0 * _proximity(float(song["acousticness"]),
                                           float(user_prefs.get("acousticness", 0.5)))

    # Tempo must be normalized to [0, 1] before proximity is meaningful.
    # Raw BPM (e.g. 140) cannot be compared directly to energy (e.g. 0.88).
    song_tempo_norm = _normalize_tempo(float(song["tempo_bpm"]))
    user_tempo_norm = (_normalize_tempo(float(user_prefs["tempo_bpm"]))
                       if "tempo_bpm" in user_prefs else 0.5)
    tempo_score        = 0.5 * _proximity(song_tempo_norm, user_tempo_norm)

    danceability_score = 0.3 * _proximity(float(song["danceability"]),
                                           float(user_prefs.get("danceability", 0.5)))

    # ------------------------------------------------------------------
    # Final score — normalize by total weight so result is in [0.0, 1.0]
    # ------------------------------------------------------------------
    weighted_sum = (genre_score + mood_score + energy_score
                    + valence_score + acousticness_score
                    + tempo_score + danceability_score)

    return round(weighted_sum / TOTAL_WEIGHT, 4)


def _explain_dict(song: Dict, prefs: Dict, score: float) -> str:
    """Build a human-readable explanation for a dict-based recommendation."""
    reasons = []

    if song["genre"] == prefs.get("genre", ""):
        reasons.append(f"genre matches ({song['genre']})")
    if song["mood"] == prefs.get("mood", ""):
        reasons.append(f"mood matches ({song['mood']})")

    energy_diff = abs(float(song["energy"]) - float(prefs.get("energy", 0.5)))
    if energy_diff <= 0.15:
        reasons.append(f"energy is close to your preference ({song['energy']})")

    if not reasons:
        reasons.append("similar audio profile to your taste")

    return "Score {:.2f} — ".format(score) + ", ".join(reasons) + "."


# ---------------------------------------------------------------------------
# OOP interface  (required by tests/test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """Content-based music recommender that ranks songs by weighted proximity to a UserProfile."""
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs sorted by weighted proximity score."""
        scored = sorted(self.songs, key=lambda s: _score_song_oop(s, user), reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation for why a song was recommended."""
        score = _score_song_oop(song, user)
        reasons = []

        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches ({song.mood})")

        energy_diff = abs(song.energy - user.target_energy)
        if energy_diff <= 0.15:
            reasons.append(f"energy is close to your target ({song.energy})")

        if not reasons:
            reasons.append("similar audio profile to your taste")

        return "Score {:.2f} — ".format(score) + ", ".join(reasons) + "."


# ---------------------------------------------------------------------------
# Functional interface  (required by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Read a songs CSV and return a list of dicts with all numeric fields cast to float."""
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["energy"]       = float(row["energy"])
            row["tempo_bpm"]    = float(row["tempo_bpm"])
            row["valence"]      = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort highest to lowest, and return the top-k as (song, score, explanation) tuples."""
    # Score every song and rank highest-to-lowest in a single expression.
    # The generator (song, score_song(...)) is consumed lazily by sorted(),
    # so no intermediate list is allocated just to be thrown away.
    ranked = sorted(
        ((song, score_song(user_prefs, song)) for song in songs),
        key=lambda pair: pair[1],
        reverse=True,
    )

    # Slice the top-k results and attach a plain-English explanation to each.
    return [
        (song, score, _explain_dict(song, user_prefs, score))
        for song, score in ranked[:k]
    ]

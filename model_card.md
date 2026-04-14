# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

A content-based music recommender that scores songs by comparing their audio
features directly against a listener's stated preferences.

---

## 2. Intended Use

VibeFinder suggests songs from a small, hand-curated catalog based on a user's
preferred genre, mood, and energy level. It is designed for classroom exploration
of how algorithmic recommendation systems work — not for deployment to real users.

- It generates a ranked list of up to five songs for a single listener session.
- It assumes the user can state their preferences explicitly (genre, mood, energy).
- It makes no use of listening history, social signals, or real-time context.
- It is intentionally simple and transparent so every recommendation can be
  traced back to a specific numerical reason.

### Non-Intended Use

VibeFinder is **not** designed for the following uses and should not be applied to them:

- **Production music services.** The catalog of 18 hand-labeled songs is far too
  small to serve real listeners. Deploying it in any live product would generate
  repetitive, low-quality recommendations.
- **Personalization over time.** The system has no memory. It cannot learn from
  a user's listening history, skips, or likes. Every session starts from zero.
- **Implicit preference inference.** VibeFinder requires the user to state their
  genre, mood, and energy explicitly. It cannot infer preferences from behavior,
  context, or listening patterns the way Spotify or YouTube do.
- **Diverse or global music discovery.** The catalog reflects Western popular
  music entirely. Using it to recommend music to listeners whose tastes include
  Latin, African, or Asian traditions would produce biased and culturally narrow
  results.
- **High-stakes filtering decisions.** Because genre and mood weights are
  hand-tuned and not validated against real user satisfaction data, the system
  should not be used to decide which artists receive promotion or which songs
  get surfaced to large audiences.

---

## 3. How the Model Works

Imagine every song in the catalog has a "file card" listing its genre, mood, and
seven audio measurements. When a user describes what they want, the system
reads every file card and awards points based on how closely each song matches.

**Genre** is worth the most points. If a user asks for lofi music, the system
strongly prefers lofi songs over everything else — similar to how a librarian
would first check the correct section of the library before comparing individual
books.

**Mood** is the second most important signal. If the user says they want something
chill, a chill song gets a bonus even if its genre is slightly different.

**Energy, valence, acousticness, tempo, and danceability** are audio measurements
on a 0-to-1 scale. For each one, the system asks: "how close is this song's
number to what the user asked for?" A song that is almost identical to the
user's target gets nearly full points; a song that is far away gets very few.

All the points are added up, divided by the maximum possible total, and the
result is a final score between 0.0 (worst match) and 1.0 (perfect match).
Songs are then sorted from highest to lowest and the top five are returned.

---

## 4. Data

The catalog contains **18 songs** stored in `data/songs.csv`.

- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop,
  r&b, hip-hop, classical, edm, country, metal, reggae, folk
- **Moods represented:** happy, chill, intense, relaxed, focused, moody,
  romantic, confident, peaceful, euphoric, nostalgic, angry, uplifted, melancholic
- The original starter file had 10 songs; 8 were added to broaden genre and mood
  coverage during development.
- The catalog is heavily weighted toward Western popular music genres. Latin,
  African, and Asian music traditions are entirely absent.
- Some genres have multiple songs (lofi has three) while most have only one.
  This means a lofi listener gets better differentiation than, say, a reggae
  listener who has only one possible genre match.
- All song features were hand-assigned, not measured from real audio. The
  numbers reflect the author's subjective interpretation of each track.

---

## 5. Strengths

The system works well when the user's preferences align with a song that clearly
dominates on multiple features at once.

- **Pop / Happy profile:** Sunrise City scored 0.99 — a near-perfect match on
  genre, mood, and energy simultaneously. The result felt immediately correct.
- **Rock / Intense profile:** Storm Runner scored 0.98 for the same reason.
  When the catalog contains an obvious match, the system finds it reliably.
- **Chill Lofi profile:** Library Rain and Midnight Coding both scored above
  0.97, and both are genuine lofi chill tracks. The top two results felt right.
- **Transparency:** Every recommendation includes a plain-English reason
  (e.g. "genre matches, energy is close to your preference"). Unlike black-box
  systems, every score can be verified by hand.
- **No cold-start problem for new songs:** Because the system scores entirely
  on audio features, a brand-new song with no listeners can still rank highly
  the moment it is added to the catalog.

---

## 6. Limitations and Bias

**Genre dominance bias**
Genre is weighted at 3.0 out of a possible 9.5 total — more than any other
single feature. This means a mediocre song in the right genre almost always
outranks an excellent song in the wrong genre. In the Sad Banger experiment,
Iron Pulse (metal / angry) scored 0.78 while Autumn Letters (folk / melancholic)
scored only 0.44 — even though Autumn Letters correctly matched the user's
stated mood. The system cannot satisfy a user who wants a specific emotional
tone within a genre that does not exist in the catalog.

**Catalog coverage bias**
A lofi listener can compare three songs against each other. A reggae listener
has only one. The quality and diversity of recommendations is structurally
unequal based purely on how many songs represent each genre. Genres with
a single entry will always return that song as their top result with no
meaningful competition.

**Binary mood and genre matching**
Genre and mood are treated as exact matches — there is no partial credit for
related categories. "Angry" and "melancholic" both score 0 for a user who
wants "focused." In reality, these moods overlap. "Relaxed" and "chill" are
near-synonyms but treated as completely different by the system.

**Neutral default bias**
When a user does not specify valence, tempo, or danceability, those features
default to 0.5. Songs near the middle of each range get a quiet boost on those
features, even when the user said nothing about them. A song might rank in the
top five not because it is a good match but because it happens to sit at the
midpoint of several unspecified dimensions.

**Collinearity between energy and acousticness**
In this catalog, high energy and low acousticness tend to go together (rock,
metal, EDM), and low energy with high acousticness also go together (lofi,
folk, classical). Because both features are scored independently, a high-energy
preference implicitly penalises acoustic songs through a second pathway, even
if the user said nothing about production style. The system effectively
double-counts the same underlying sonic dimension.

---

## 7. Evaluation

### Profiles Tested

Eight profiles were run against the 18-song catalog: three standard profiles
and five adversarial edge cases designed to expose failure modes.

| Profile | What it tested |
|---|---|
| Pop / Happy | Baseline — does the obvious match surface first? |
| Rock / Intense | Opposite energy and acoustic space from lofi |
| Chill Lofi | Low-energy, high-acoustic end of the feature space |
| Ghost Profile | No genre or mood — pure audio proximity only |
| Sad Banger (metal + melancholic) | Genre and mood pointing to different songs |
| Acoustic Rager (rock + acousticness=0.90) | Contradictory numeric preferences |
| Catalog Gap (classical + angry) | Impossible combination in catalog |
| Energy Paradox (lofi + energy=0.95) | Genre dominance vs numeric mismatch |

### Results and Surprises

**What worked as expected**
The three standard profiles all returned their obvious top match with scores
above 0.97. This was the expected baseline result.

**The Gym Hero problem**
For the Pop / Happy profile, *Gym Hero* ranked second at 0.74. Gym Hero is
a pop song (genre match) with high energy (energy=0.93, close to the user's
0.80), but its mood is "intense" not "happy." The system surfaced it because
it earned full genre points and near-full energy points — enough to outscore
any non-pop song even with a mood mismatch. A human playlist curator would
not include a workout anthem in a happy pop playlist. This is the clearest
example of the system doing the right thing mathematically but the wrong
thing musically.

**The Ghost Profile was the most revealing**
When genre and mood were removed entirely, the top score was only 0.42.
The five results spanned country, lofi, r&b, and synthwave — genres with
nothing in common. The system had no preference signal to work with and
just surfaced whatever happened to sit closest to the midpoint of the
feature space. The recommendations were not wrong in any measurable way,
but they were completely meaningless as music suggestions. This confirmed
that categorical signals (genre and mood) carry most of the system's
useful information.

**The Energy Paradox was the most counterintuitive**
A user who said they wanted `energy=0.95` (EDM-level intensity) received
*Library Rain* and *Midnight Coding* — both very quiet lofi tracks with
energy around 0.35–0.42. This is because genre and mood together are worth
5.0 points, while the energy mismatch penalty reduces the score by only
about 0.84 points. The categorical match dominated so strongly that the
system recommended the opposite of what the user described in audio terms.

**What the weight-swap experiment showed**
Doubling energy (1.5 → 3.0) and halving genre (3.0 → 1.5) while keeping
the total at 9.5 produced almost no change in rankings for the standard
profiles, because songs that match genre tend to also be close in energy.
The only meaningful change appeared in the Energy Paradox profile, where
the lofi songs dropped from 0.90 to 0.81 — still ranked first, but with
less confidence. The experiment showed that the current rankings are
driven more by the structure of the catalog (what songs exist and how
similar they are within genres) than by the specific weight values chosen.

---

## 8. Future Work

- **Partial credit for related genres and moods.** "Angry" and "melancholic"
  should not both score 0 for a user who wants "intense." A small similarity
  table would resolve the Sad Banger failure case.
- **Weighted mood within genre.** If genre matches, mood should carry more
  relative weight within that narrowed candidate set. Right now mood is
  treated the same whether or not genre already matched.
- **Diversity constraint.** The system will recommend three lofi songs in a
  row for a lofi listener. A real recommender would enforce at least one song
  from an adjacent genre to avoid a genre echo chamber.
- **Audio feature measurement instead of hand-assignment.** Real values from
  a music analysis API (like Spotify's audio features endpoint) would make the
  catalog numbers objective and comparable.
- **Expanded catalog.** 18 songs is too small for meaningful differentiation.
  With fewer than two songs per genre on average, catalog coverage bias
  dominates the results.

---

## 9. Personal Reflection

**What was your biggest learning moment?**

The biggest learning moment was the weight-swap experiment. I expected that
doubling energy's weight and halving genre's weight would meaningfully change
the rankings — instead almost nothing moved. That forced me to investigate why,
and I discovered that the catalog's songs are naturally clustered: rock songs
tend to be high-energy and low-acoustic, lofi songs tend to be low-energy and
high-acoustic. The genre label and the audio numbers encode nearly the same
information. Removing the genre label entirely (Ghost Profile) was far more
disruptive than any weight change I tried. The lesson: in a small, structured
catalog, *what data you have* matters more than *how you weight it*.

**How did using AI tools help you, and when did you need to double-check them?**

AI tools were most useful for generating boilerplate — the initial song CSV rows,
the Mermaid flowchart skeleton, and the scoring formula structure all came
together quickly with AI assistance. The place where I had to slow down and
verify was any time the AI suggested a specific numeric value or made a claim
about what the system would output for a given profile. Several times the
predicted scores were slightly off because the AI was reasoning about the formula
in general terms rather than computing it precisely. The rule I settled on: use
AI to draft structure and explain concepts, then run the actual code to verify
any specific number the AI states.

**What surprised you about how simple algorithms can still "feel" like recommendations?**

The Pop / Happy profile returning *Sunrise City* at 0.99 felt immediately right —
it matched genre, mood, and energy at the same time, and the explanation
("genre matches, mood matches, energy is close") read like something a human
playlist curator would say. That surprised me because the underlying math is just
seven multiplications and an addition. There is no understanding of music at all.
What makes it feel like a recommendation is that the *labels* (genre, mood) are
human judgments baked into the data — the algorithm is just retrieving those
judgments and presenting them as if it reasoned about them. The "intelligence"
lives in whoever assigned "pop / happy" to the song, not in the formula.

**What would you try next if you extended this project?**

The single change I would make first is partial credit for related moods and
genres. "Angry" and "melancholic" should not both score 0 for a user who wants
"intense" — a small similarity table (e.g., angry=0.4, sad=0.3 when intense is
requested) would resolve the Sad Banger failure case without changing the
architecture at all. After that, I would replace hand-assigned audio numbers with
real values from a music analysis API so the features are objective and
comparable across songs added by different people.

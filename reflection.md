# Profile Reflection: Comparing Outputs

This file documents what each pair of user profiles revealed about the
recommender system — written in plain language for anyone who has not
read the code.

---

## Pair 1: Pop / Happy vs. Rock / Intense

**Pop / Happy top result:** Sunrise City (score 0.99)
**Rock / Intense top result:** Storm Runner (score 0.98)

These two profiles sit at opposite ends of the catalog. Sunrise City is
bright, upbeat pop at 118 BPM. Storm Runner is distorted, fast rock at
152 BPM. The system correctly separated them and surfaced a different #1
for each, which is exactly what it is supposed to do.

The interesting part is what shows up at #2 for each:

- The pop listener gets *Gym Hero* at 0.74. Gym Hero is a pop song, so it
  earns genre points. Its energy (0.93) is also close to what the user wanted
  (0.80). But its mood is "intense," not "happy." The system does not care —
  it gave full marks for genre and almost full marks for energy, and that was
  enough. In plain terms: **the system knows Gym Hero is pop music, but it
  does not know that "intense pop" and "happy pop" are different feelings.**
  A human playlist curator would keep Gym Hero off a happy playlist. The
  algorithm would not.

- The rock listener gets *Gym Hero* at #2 as well (0.62) — this time for its
  mood ("intense" matches) and high energy. One song sitting in the top two
  for completely different listener types is a sign that Gym Hero is sitting
  in a "universal second place" region of the feature space where it benefits
  from both genre signals and energy proximity regardless of who is asking.

---

## Pair 2: Chill Lofi vs. Energy Paradox

**Chill Lofi top result:** Library Rain (score 0.99)
**Energy Paradox top result:** Library Rain (score 0.90)

These two profiles share the same genre (lofi) and mood (chill) but ask for
completely different energy levels: 0.38 vs. 0.95.

Library Rain has energy=0.35 — perfect for the chill listener and completely
wrong for someone who said they want near-maximum energy. Yet Library Rain
ranks #1 for both.

**Why does this happen?**

Think of it like a loyalty card. Matching genre earns 3.0 points and matching
mood earns 2.0 points — a combined 5.0 out of 9.5 total. The energy mismatch
for the Energy Paradox listener costs about 0.8 points. The genre+mood loyalty
bonus (5.0) is simply too large for any energy penalty to overcome.

In plain terms: **the system is so loyal to genre that it will recommend a
quiet lofi track to someone who said they want high energy, just because they
also said they like lofi.** If you tell the system "I want lofi at EDM energy
levels," it hears the "lofi" part loudly and the "EDM energy" part quietly.

This is a real failure mode. Real recommenders handle it by treating the energy
request as a filter first, then applying genre preference within the filtered
set.

---

## Pair 3: Sad Banger vs. Catalog Gap

**Sad Banger:** genre=metal, mood=melancholic → top result: Iron Pulse (metal / angry) at 0.78
**Catalog Gap:** genre=classical, mood=angry → top result: Quiet Arpeggios (classical / peaceful) at 0.71

Both profiles asked for a combination that does not exist in the catalog:
no metal+melancholic song, no classical+angry song. The system had to
make a decision: honour the genre or honour the mood?

In both cases, **genre won.**

- Iron Pulse (metal) beat Autumn Letters (folk / melancholic) because the genre
  match (3.0 points) outweighed the mood match (2.0 points).
- Quiet Arpeggios (classical) beat Iron Pulse (metal / angry) because, again,
  the classical genre match was worth more than the angry mood match.

In plain terms: the system treats genre like a hard filter and mood like a
soft preference. When they conflict, genre always wins.

Is that the right call? For most listeners, probably yes — recommending rock
to someone who wants lofi is usually worse than recommending the wrong mood
within lofi. But for a user specifically seeking an emotional tone (melancholic,
angry), it produces results that feel musically wrong even when they are
mathematically correct.

The deeper issue is that **some moods are bound to genres in the real world.**
Melancholic music and metal do co-exist (doom metal, post-metal, black metal).
But none of those nuances exist in an 18-song catalog, so the system cannot
find them.

---

## Pair 4: Ghost Profile vs. Any Standard Profile

**Ghost Profile top result:** Dusty Roads (country / nostalgic) at 0.42
**Pop / Happy top result:** Sunrise City (pop / happy) at 0.99

The gap between these two top scores — 0.42 vs. 0.99 — is the clearest way
to see how much of the system's usefulness comes from genre and mood.

When you specify genre and mood, the system has a strong signal. The top score
is usually above 0.95 and the top result is obvious. When you strip genre and
mood away (Ghost Profile), the highest possible score collapses to around 0.42
and the results look random — country, lofi, r&b, and synthwave in the same
top five, with no common thread.

**Why does Dusty Roads win the Ghost Profile?**
It has energy=0.50 — an exact match for the target of 0.50. Its valence (0.64),
acousticness (0.80), and tempo are all reasonably close to their 0.5 defaults.
Dusty Roads is not a good recommendation for anyone in particular. It just
happens to sit near the mathematical centre of the feature space.

In plain terms: **without genre and mood, the system becomes a "find the most
average song" machine.** The winner is not the best song — it is the most
middling one. This shows that categorical labels (genre, mood) are carrying
almost all of the system's real intelligence. The audio numbers alone are
not enough to give the recommendations meaning.

---

## Pair 5: Acoustic Rager vs. Rock / Intense

**Acoustic Rager:** rock/intense + acousticness=0.90 → Storm Runner (score 0.90)
**Rock / Intense:** rock/intense + acousticness=0.10 → Storm Runner (score 0.98)

Same genre, same mood, same energy — but one profile asked for acoustic
production (0.90) and one asked for electric/distorted (0.10). Storm Runner
has acousticness=0.10, making it a perfect acoustic match for the standard
rock listener but a poor match for the Acoustic Rager.

Storm Runner still ranked #1 for both.

**Why?**
The acousticness mismatch for the Acoustic Rager (wanting 0.90, getting 0.10)
costs about `1.0 × (1 − 0.80) = 0.20` points. But Storm Runner's
genre+mood+energy match is worth so much that 0.20 points of penalty barely
moves the score: from 0.98 down to 0.90.

In plain terms: **you can ask for acoustic rock and get electric rock because
the system treats genre and energy as so important that a production-style
mismatch is a minor inconvenience, not a dealbreaker.** A user who wants
a genuine acoustic rock sound — fingerpicked guitar, no distortion — would
be poorly served by this result. The system literally cannot tell the
difference between acoustic and electric rock as long as both are labeled
"rock."

The score dropped from 0.98 to 0.90, which shows the acousticness preference
did register. But it was not nearly enough to surface a different song in
#1 position. There is no acoustic rock song in the catalog to surface anyway,
which is also part of the problem.

# Model Card: Music Matcher 2.0 (Agentic Reliability Harness Integration)

## 1. Model Name

**Music Matcher 1.1: A self-tuning music recommender with a bounded self-checking reliability workflow.**

This is the Applied AI (Module 4) variation of the Module 1–3 "Music Recommender Simulation." While core deterministic scorer logic is unchanged, the new version adds a reliability / testing system and a bounded agentic workflow on top.

---

## 2. Intended Use

Music Matcher is a classroom exploration of:
(1) How a recommender can measure its own quality against human-labeled rankings
(2) How a small bounded agent can self-tune scoring weights without breaking invariants. 
Intended users are students and instructors studying applied AI; it is **not** a production system. It assumes CLI use, a small curated catalog, and no real users, no API calls, no network access.

---

## 3. How the Model Works

The model is a **content-based, weighted linear recommender** with a reliability + agent layer wrapped around it.

1. A `UserProfile` (weighted genre/mood preferences, target audio values, liked/disliked history, artist affinity) and the 20-song `data/songs.csv` are the inputs.
2. `score_song(user, song, config)` combines: weighted genre/mood match, per-feature audio similarity (energy, tempo, valence, danceability, acousticness), like/dislike deltas, and artist affinity. Weights come from a `ScoringConfig` dataclass rather than hardcoded constants so they can be logged, compared, and tuned.
3. `recommend_songs` validates the profile, scores every song, sorts descending, returns top-k plus a short reason string, and logs a JSON record with profile hash / top ids / top scores / warnings / latency to `logs/recommender.jsonl`.
4. `src/eval.py` evaluates any `ScoringConfig` against `data/eval_profiles.json` to produce nDCG@5, precision@5, recall@5, coverage, and genre entropy.
5. `src/agent.py` runs a **plan -> act -> check -> decide** loop: pick a random weight, change different weights by ±step_size, re-evaluate, accept if metrics did not regress and no guardrail fired; otherwise roll back. Every step is logged to `logs/agent.jsonl`.
6. `src/main.py` exposes three CLI modes: default demo, `--tune` (loads the agent's saved config), and `--interactive` (human feedback loop that reuses the same validate-then-semantic-check pattern the agent uses).

---

## 4. Data

- **Catalog:** 20 songs in `data/songs.csv`. Each song has id, title, artist, genre, mood, and five audio features (energy, tempo_bpm, valence, danceability, acousticness, all scaled as in Spotify-style metadata). Genres span pop, lofi, ambient, jazz, rock, metal, classical, synthwave, house, hip hop, reggaeton, folk, country, afrobeat, blues, drum and bass, indie pop.
- **Evaluation baseline:** 5 profiles in `data/eval_profiles.json`, each with a relevance dictionary mapping song id -> 0/1/2. The labeling rubric (embedded in the JSON itself): `relevance = 2` when the song's genre AND mood both match the profile's preferences; `relevance = 1` when exactly one matches; omitted ids are treated as 0.
- **Size is a known limit.** 5 profiles × 20 songs cannot capture real-world taste diversity, the model card treats this as a structural limitation (Section 6) and the agent's tuned weights are explicitly noted to be overfit to this set.
- **No audio-analysis pipeline.** Numeric features were authored by hand to be plausible for each genre; production systems would compute them from audio.

---

## 5. Strengths

- **Explainable.** Every recommendation carries a reason string (`+1.25 genre:lofi; +2.00 mood:chill; +3.88 energy similarity`) and every agent decision carries a `reason` field in its log line.
- **Measurable.** nDCG, precision, recall, coverage, genre entropy give per-profile and system-level views. `evidence/eval_latest.md` regenerates on demand.
- **Reproducible.** Seeded RNG in the agent means `python -m src.agent --seed 0 --budget 20` produces identical step logs on any machine.
- **Defensive.** Runtime validation rejects out-of-range inputs and warns on contradictions. Golden regression snapshots catch unintended ranking drift. Property tests (`hypothesis`) assert invariants across hundreds of random inputs.
- **Integrated.** The tuned config the agent produces is loaded by the default CLI via `--tune`, and the interactive mode uses the same validation layer as the agent. The reliability feature is not a side script and reaches all areas of this project.

---

## 6. Limitations and Bias

- **Tuning overfits the 5 labeled profiles.** After 30 agent iterations (seed=1, step=0.5), mean nDCG climbed from 0.9429 to 0.9786, but measured only on the same 5 profiles that drove the decisions. With no held-out set, that number overstates generalization.
- **Zeroed weights could hurt unseen users.** The tuned config zeros `w_dance` and `w_acoustic` and reduces `w_tempo` to 0.2. These weights may be essential for user types not represented in our 5 profiles (e.g., someone who explicitly cares about danceability).
- **Subjective labels.** I wrote the relevance grades. "Vibrant afrobeat" for a happy-pop profile could be a 2, a 1, or a 0 depending on the grader's priors. The labeling rubric is documented in `eval_profiles.json` but is still inherently subjective.
- **Small catalog bias.** Genres represented by 1-2 songs get a lot of per-song weight in the metrics; a drop in one song's rank can swing a profile's nDCG by several points.
- **No understanding of lyrics or cultural context.** A sad-sounding song about recovery is indistinguishable from a sad song about heartbreak.
- **Conflicting signals handled naively.** If a user likes and dislikes the same song id, the system emits a warning and applies both `+w_liked` and `+w_disliked` to the score, letting the numbers cancel. That's deterministic but probably wrong in practice as real users contradict themselves, and the system should take the most recent signal.
- **Interactive mode trusts a typed song id.** `like 3` adds id 3 to the liked list without confirming that 3 is the song the user is looking at. A mismatched display could let someone accidentally like the wrong song.

---

## 7. Evaluation

### Metrics used

- **nDCG@:** per-profile ranking quality.
- **Precision@5 / Recall@5:** per-profile relevant-in-top-5 coverage.
- **Coverage:** system-level catalog exposure across all profiles.
- **Genre entropy:** per-profile diversity (bits).

### Results

| Metric | Default config | Agent-tuned config | Δ |
| --- | ---: | ---: | ---: |
| mean_ndcg       | 0.9429 | 0.9786 | +0.0357 |
| mean_precision  | 0.9200 | 1.0000 | +0.0800 |
| mean_recall     | 0.7129 | 0.7929 | +0.0800 |
| coverage        | 0.9000 | 0.8500 | −0.0500 |
| guardrail / invariant violations | 0 | 0 | 0 |

The `Night Drive Moody` profile saw the biggest individual gain (nDCG 0.7929 → 0.9714) because the default weights over-penalized it; the tuning run specifically adjusted `w_mood`, `w_artist`, and `w_valence` in its favor. Coverage dropped slightly because the tuned config concentrates recommendations on stronger matches which is a classic precision/coverage trade-off.

### Test suite

- 49 tests across 6 files (`test_recommender.py`, `test_validation.py`, `test_eval.py`, `test_properties.py` with hypothesis, `test_regression.py` with golden snapshots, `test_agent.py`, `test_feedback.py`). Runs in ~0.5 s.
- Property-based tests assert determinism, like monotonicity, dislike monotonicity, and genre-weight monotonicity across ~100 random inputs each.
- Golden regression tests pin the top-5 per profile; deliberate tampering reproducibly fails with a readable diff.
- Agent tests assert bounds-respecting behavior, improvement from a zeroed starting config, same-seed reproducibility, and different-seed divergence.

### Surprises

- Running the agent with default `step_size=0.25` produced zero improvement across all 10 seeds I tested. The default config is at a strong local maximum; the agent needed `step_size=0.5` to escape. This is an honest limitation of hill-climbing that smarter optimizers (simulated annealing, Bayesian) would reduce.
- The genre-monotonicity property test is a guardrail for features *not yet implemented* — if someone adds a diversity penalty later and it inadvertently causes raising a genre weight to lower a song's rank, the test will fail loudly.

---

## 8. Future Work

- **Held-out evaluation set.** Split the 5 profiles into 3 train / 2 test. Report agent improvement on both and only trust the held-out number. Required to honestly claim generalization.
- **Smarter optimizer.** Swap hill climbing for simulated annealing or Bayesian optimization (`scikit-optimize`) to escape local maxima without hand-tuning step size.
- **Catalog growth.** Expand `songs.csv` to 100+ songs with real audio-feature extraction; re-label a proportionally larger evaluation set.
- **Signed tuned configs.** Sign `evidence/tuned_config.json` and log its hash on every `--tune` startup so nobody can substitute a modified config silently.
- **Recency-weighted feedback.** Replace the naive like/dislike dual-application with a recency-based rule so the latest signal wins.
- **Cohort-aware defaults.** Ship a map of `{cohort -> ScoringConfig}` so the tuned weights for one population don't degrade experience for another.
- **Streamlit dashboard.** A slider-per-weight UI to visualize how changes shift the top-5 live, using the same `recommend_songs` API.

---

## 9. Personal Reflection

This project taught me that when constructing/expanding on test harnesses or agentic processes, the difficult portion of implementation is the process of verification and replication. Even after phases of the project where the code is completed and I understood how the system works, there were layers of robustness that had to be added like validation, metrics, invariant rule tests, golden snapshots, agent logging, and regression measurement. However, since all of this was added by the time the agent was implemented, each one of those layers helped catch edge cases when validation the agent changes, which made the process smooth towards the end.

Surprisingly, the agent itself was smaller than I expected, in part due to implementing a more simpler and deterministic type rather than true agentic workflows that utilize framework SDKs, LLMs, and MCPs. Additionally the whole `WeightTuningAgent` class is under 200 lines, but what makes it emulate intelligence is the loop it iterates, the seeded RNG, and logged trajectory. All of that came from the reliability system built around it which was the main portion of the work and something I will carry into the future when working in applied-AI sectors.

The biggest thing that surprised me was the how true the saying "less is more" continues to show up in everything I do. Things like keeping the score deterministic instead of learned, keeing the agent's retries bounded to zero (no replan on failure), and keeping the feedback parser simple about the catalog. Most times where I thought a complicated solution would be needed, the simpler one tended to be more defensible and easier to integrate. Applied AI isn't about making the AI do more, but about making the boundaries around it tight enough to trust which is where agent SDKs like NVIDIA's NeMo or Amazon's Strand come in.

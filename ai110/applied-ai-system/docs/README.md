# Music Matcher - A Self-Tuning Music Recommender with a Bounded Reliability Workflow

> *"A system that measures, adjusts weights, and checks by itself before answering."*

---

## Original Project (Module 3)

The original project built during Modules 3 was the **Music Recommender Simulation**, a basic CLI music recommender for AI110. It represented songs and a user taste profile as dataclasses, used a weighted linear scoring rule (genre, mood, target audio features, liked/disliked history) to rank a 20-song catalog, and output the results in the terminal which displayed the top-5 recommendations for five named preference profiles. However, that was it's only function, there was no way to measure recommendation quality, runtime validation, and self tuning mechanism for improvement.

## Applied AI System (Module 4)
The purpose of this Applied AI project is to extend that base created into a reliability-driven, self-tuning system that didnt replace the core scoring logic. And so while the determinisitc attribute weighted calcuations are stil present, the added content exists to make the system overall robust and to further increase the accuracy of that algorithm, showing how even a basic agent loop and reliability harness and drastically improve a relatively simple system. One thing to note is that this project will be focusing on the more classical/linear AI with a simple agent layer rather than the more mainstream ideas like cloud-based LLMs and complex agentic loops, the reason being that I have not touched agents and agentic system prior so a more fundamental approach will help me learn the foundations, which it did.

---

## Title and Summary

**Music Matcher 1.1: A self-tuning music recommender with a bounded self-checking reliability workflow.**

Music Matcher incorporates 2 of the 4 features listed in Project 4's overview:
1. **A Test Harness/Evaluation Script** that measures recommendation quality against established baselines (nDCG, precision, recall, coverage, genre entropy), enforces invariants at runtime (input validation, structured JSON logs, property-based tests, golden regression snapshots), and surfaces warnings as priority output.
2. **An agentic workflow** where a bounded plan loops over act -> check -> decide, more in depth goes through the cycle of perturbing scoring weights, re-evaluating against the reliability system, and accepting only changes that improve measured quality without breaking invariants, which are rules that remain true throughout program execution.

This matters because it shows that a recommender that can't measure itself can't improve. Giving the system an objective function, guardrails, and a small decision loop turns it from a static scorer into an auditable, dynamic learner, even while keeping the heuristic core algorithm.

---

## Architecture Overview

Four layers sit between user input and output (see [UML.md](UML.md) for the full diagram):

1. **Core scorer** (`src/recommender.py`, `src/config.py`): Deterministic weighted scorer where weights were changed into a `ScoringConfig` dataclass so they can be passed, logged, and tuned vs the hardcoded weights from the previous project.
2. **Reliability layer** (`src/eval.py`, `src/logging_utils.py`, `UserProfile.validate()`): Computes the ranking metrics against `data/eval_profiles.json`, validating all inputs at runtime, and writes JSONL logs (`logs/recommender.jsonl`) for every recommendation.
3. **Agent layer** (`src/agent.py`): `WeightTuningAgent` incrementally attepts to optimize relevancy and scores using `ScoringConfig`, utilizing the reliability layer as its objective and guardrail. Every iteration is logged to `logs/agent.jsonl`, while the final report is displayed in `evidence/agent_report.md`.
4. **CLI dispatcher** (`src/main.py`): Alls the user to run three modes via CLI: the default demo, flag `--tune` (loads the agent's tuned config but runs the agent if no tuned config is available), and flag `--interactive` (a human feedback loop that uses the validation layer as a live guardrail).

So if data flow had to be summarized into one sentence, it would be: **user input -> validate -> score with a ScoringConfig -> return ranked results + log everything while the agent closes the loop by evaluating candidate configs against labeled data and promoting winners.**

---

## Setup Instructions assuming Miniforge/Conda

### 1. Activate the conda environment

The project expects Python 3.10+ and `hypothesis` for property tests.
```bash
conda activate codepath
pip install -r requirements.txt
```

### 2. Verify the green baseline

```bash
pytest -q                      # expected result: 49 passed
```

### 3. Run the recommender in each mode

```bash
python -m src.main             # default demo: 5 profiles, original config
python -m src.main --tune      # same demo, but with the agent's tuned config
python -m src.main --interactive --profile "Chill Lofi"   # human feedback loop
```

### 4. Run the reliability harness

```bash
python -m src.eval             # writes evidence/eval_latest.md
```

### 5. Run the agent

```bash
python -m src.agent --budget 30 --seed 1 --step-size 0.5 \
                    --save-config evidence/tuned_config.json
```
Outputs: `logs/agent.jsonl` (one JSON line per iteration) and `evidence/agent_report.md` (summary + trajectory).

#### 5.1 CLI flag reference

To clarify what each flag adjusts in the agent, the table below provides an explanation for each.

| Flag | Default | What it controls |
| --- | --- | --- |
| `--budget` | `20` | Maximum number of **plan -> act -> check -> decide iterations** the loop may run. Iteration in this case means one full cycle of picking a weight, proposing a change, re-evaluating all 5 profiles, and deciding to keep or roll back. The loop can still stop earlier if `--patience` triggers. |
| `--seed` | `0` | RNG seed that determines **which weight gets picked each iteration** and **whether the delta is positive or negative**. Used for reproducibility. The value itself has no meaning and is just a label for a specific search path through the weight space. |
| `--step-size` | `0.25` | Magnitude of each weight adjustment. Small steps have the possibility of plateauing while large steps can overshoot. This project's default shows how `0.25` hits the local maximum, where any change doesn't improve, while `0.5` does positively affect the results. |
| `--patience` | `5` | **Early-stopping threshold,** where if X many consecutive iterations pass without a *strict* improvement in `mean_ndcg`, the loop stops and logs `"reason": "patience_exhausted"`. This prevents pointless computation once the agent is stuck. |
| `--k` | `5` | Top-k cutoff passed to `recommend_songs()` during each check, which in this case means every evaluation score the top-5 ranking against the labels. Changing this will change what "quality" means (top-3 vs top-10 is a different objective). |
| `--eval-path` | `data/eval_profiles.json` | Where to load the hand-labeled profiles and relevance grades from. |
| `--songs-path` | `data/songs.csv` | The song catalog to rank. |
| `--log-path` | `logs/agent.jsonl` | Destination for per-iteration JSON records (`agent_start`, `agent_step`, `agent_stop`). |
| `--out` | `evidence/agent_report.md` | Path for the markdown report with config diff, accepted-action table, and ASCII trajectory chart. |
| `--save-config` | *(none)* | If provided, writes the final tuned `ScoringConfig` as JSON to this path. This is the file `python -m src.main --tune` reads at startup. Without this flag the tuned weights are lost after the run ends. |

#### 5.2 Vocabulary used in the log and report

| Term | Meaning |
| --- | --- |
| **Accepted (tied)** | A change that didn't worsen `mean_ndcg` or improve it either. Intended by design so the agent can move across plateaued weight changes to see if can reach a breakpoint. However, those plateaus are what `patience` counts, and are rolled back if enough weights meet the threshold. |
| **Rollback** | When `decide()` rejects a candidate, `current` stays unchanged; the rejected config never becomes the baseline for the next iteration. |
| **logs/agent.jsonl** | A `.gitigored` file that contains one JSON object per line to easily `grep`, `jq`, or load into pandas. |
| **evidence/tuned_config.json** | The agent's output config, utilized by `python -m src.main --tune`. |

#### 5.3 Reproducibility

The entire run is a deterministic function of `(starting_config, seed, step_size, budget, patience, eval_path, songs_path, k)`. Running `python -m src.agent --budget 30 --seed 1 --step-size 0.5` on any machine produces the same `logs/agent.jsonl` (modulo timestamps) and the same `evidence/tuned_config.json`. This is verified by the test `test_same_seed_yields_identical_step_log` in `tests/test_agent.py`.

### 6. Re-record golden regression snapshots (only when intentional)

```bash
UPDATE_GOLDEN=1 pytest tests/test_regression.py
```

`UPDATE_GOLDEN` is an environment variable read by `tests/test_regression.py`. Setting it to `1` tells the test to **overwrite** each profile's snapshot with the current top-5 instead of comparing against the saved one. Only use it when you have deliberately changed scoring behavior and want the new output to become the new baseline, otherwise the snapshots exist to catch unintended drift.

---

## Sample Interactions

### Interaction 1: Default demo (`python -m src.main`)

Top 5 for the `Chill Lofi` profile scored with the baseline `ScoringConfig()`:

```
=== Chill Lofi ===
Rank  ID   Title                   Score   Reasons
----------------------------------------------------------------------
1     4    Library Rain            11.22   +1.25 genre:lofi; +2.00 mood:chill; +3.88 energy similarity
2     2    Midnight Coding         11.05   +1.25 genre:lofi; +2.00 mood:chill; +3.84 energy similarity
3     9    Focus Flow              10.83   +1.25 genre:lofi; +1.60 mood:focused; +3.92 energy similarity
4     6    Spacewalk Thoughts      10.29   +1.00 genre:ambient; +2.00 mood:chill; +3.60 energy similarity
5     7    Coffee Shop Stories      9.47   +0.50 genre:jazz;  +1.20 mood:relaxed; +3.96 energy similarity
```

### Interaction 2: Tuned mode (`python -m src.main --tune`)

After running the agent with `seed=1 step_size=0.5`, the tuned config is loaded from `evidence/tuned_config.json`. Mean nDCG across all 5 profiles increased from `0.9429 -> 0.9786` and precision from `0.92 -> 1.00`. The biggest improvment is for `Night Drive Moody`, which jumps from `0.7929 -> 0.9714`:

```
=== Night Drive Moody (tuned) ===
Rank  ID   Title                   Score   Reasons
----------------------------------------------------------------------
1     8    Night Drive Loop         ...    genre:synthwave; mood:moody
2     19   Midnight Circuit         ...    genre:house
3     11   City Cipher              ...    mood:confident (now surfaces via w_artist bump)
4     3    Storm Runner             ...    genre:rock
5     9    Focus Flow               ...    mood:focused
```

### Interaction 3: Interactive feedback (`python -m src.main --interactive --profile "Chill Lofi"`)

Typed input is parsed, validated, and semantically checked before being committed:

```
feedback? like 12                  -> accepted: LikeSong
feedback? dislike 5                -> accepted: DislikeSong
feedback? more acoustic            -> accepted: AdjustTarget (target_acousticness +0.10)
feedback? like 999                 -> rejected: id not found in catalog
feedback? nonsense                 -> rejected: parse_unknown
feedback? done                     -> done.
```

The matching log entries in `logs/agent.jsonl`:

```json
{"event": "interactive_accepted", "action": "LikeSong",     "details": {"song_id": 12}}
{"event": "interactive_accepted", "action": "DislikeSong",  "details": {"song_id": 5}}
{"event": "interactive_accepted", "action": "AdjustTarget", "details": {"field": "target_acousticness", "delta": 0.1}}
{"event": "interactive_rejected", "action": "LikeSong",     "reason": "song id 999 not found in catalog"}
{"event": "interactive_rejected", "raw": "nonsense",        "reason": "parse_unknown"}
{"event": "interactive_done"}
```

---

## Design Decisions

**1. Dynamic Weights:** Moving hardcoded `W_*` constants into a `ScoringConfig` dataclass was the most important change as without it, the agent, eval reports, and tuned configs are not possible. The trade-off is that every scoring function now needs a `config` parameter, but it defaults to `None` -> `ScoringConfig()` so old call sites remain unchanged.

**2. Keeping the ranking engine deterministic:** The agent tunes weights around the scorer rather than replacing it with anything stochastic like ML algorithms. While this stopped me from utilizing learned embeddings, this helped show how the original system from Project 3 could be improved and also was a good way to introduce me into the simpler side of agents since I had not touched the topic prior.

**3. Severity-split validation:** Hard violations raises like out-of-range numbers versus contradictions such as `liked ∩ disliked` that just warn.While this required more effort, this prevented CLI crashing on realistic terminal input, which would defeat integration.

**4. Three-layer feedback pipeline for the interactive mode:** Parser -> validator -> semantic check. The issues lies in having three chances for an error to be caught in the wrong layer, this was minimized by keeping each layer's responsibility constricted (grammar vs bounds vs catalog membership).

**6. Golden regressions with an escape hatch:** `UPDATE_GOLDEN=1 pytest` is the only way to overwrite snapshots, where setting it to anything other than the string "1" performs a normal comparison, preventing excess maintainance when trying to do either overwrite or just comparison.

---

## Testing Summary

The reliability system is based on four factors:

- **Automated tests:** 49 tests across 6 files (recommender contract, validation, eval metrics, property invariants, golden regression, agent contract, feedback parser + interactive integration) that runs in under half a second.
- **Confidence scoring:** `mean_ndcg` plays the role of the system's self-reported confidence. It averages `0.9429` under the default config and `0.9786` after the agent tunes, with zero guardrail violations across all 5 evaluation profiles (`report.passed == True`).
- **Logging and error handling:** Every `recommend_songs` call produces a JSON line in `logs/recommender.jsonl` with profile hash, top ids, scores, warnings, and latency. The agent also produces matching lines in `logs/agent.jsonl`, where any raised validation error is also logged with `event: "recommend_failed"`.
- **Human evaluation:** Labeled `data/eval_profiles.json` with the labeling rubric written into the file itself (`relevance=2` when genre AND mood match, `relevance=1` for single-field match), which is what defines "better" for the agent. Additionally reviewed the generated `evidence/eval_latest.md` and `evidence/agent_report.md` after each agent or user-driven run.

**Summary in one line:** 49 of 49 tests pass, confidence (mean_ndcg) averaged 0.9429 on the default config and improved to 0.9786 after agent tuning, the interactive layer caught and logged every malformed input during testing, and the AI struggled earliest when context was ambiguous (labeling `Night Drive Moody` subjectively because only one song perfectly matched reflection.md contains a much more in depth explanation).

---

## Reflection

### What this project taught me about AI and problem solving

This project taught me that when constructing/expanding on test harnesses or agentic processes, the difficult portion of implementation is the process of verification and replication. Even after phases of the project where the code is completed and I understood how the system works, there were layers of robustness that had to be added like validation, metrics, invariant rule tests, golden snapshots, agent logging, and regression measurement. However, since all of this was added by the time the agent was implemented, each one of those layers helped catch edge cases when validation the agent changes, which made the process smooth towards the end.

Surprisingly, the agent itself was smaller than I expected, in part due to implementing a more simpler and deterministic type rather than true agentic workflows that utilize framework SDKs, LLMs, and MCPs. Additionally the whole `WeightTuningAgent` class is under 200 lines, but what makes it emulate intelligence is the loop it iterates, the seeded RNG, and logged trajectory. All of that came from the reliability system built around it which was the main portion of the work and something I will carry into the future when working in applied-AI sectors.

The biggest thing that surprised me was the how true the saying "less is more" continues to show up in everything I do. Things like keeping the score deterministic instead of learned, keeing the agent's retries bounded to zero (no replan on failure), and keeping the feedback parser simple about the catalog. Most times where I thought a complicated solution would be needed, the simpler one tended to be more defensible and easier to integrate. Applied AI isn't about making the AI do more, but about making the boundaries around it tight enough to trust which is where agent SDKs like NVIDIA's NeMo or Amazon's Strand come in.

### Limitations and biases

- **Tuned on 5 profiles only:** The agent's final weights (w_dance=0, w_acoustic=0, w_tempo=0.2) reflect what helps these specified labels, and could hurt users whose preferences lean on the mentioned weights.
- **Subjective labels:** The relevance grades in `eval_profiles.json` are based off my opinion. Two reviewers could disagree about whether "vibrant/afrobeat" counts as a 2 or 1 for a pop profile.
- **Small catalog:** 20 songs cannot represent real taste diversity.
- **No cultural/lyrical understanding:** The scorer sees `mood: "happy"` but has no idea what the song is actually about, though the other weights/attributes should help in narrowing that down.
- **Synthetic audio features:** Energy/valence numbers were authored both the original repository and by LLM for additional songs to be plausible, in production these come from audio analysis with its own biases.

### Could this AI be misused?

The most plausible misuse is weight adjusting to hide content, where a malicious operator could:

- Set `w_disliked` to `0.0` instead of `-4.0`, silently disabling every user's "blocked songs" list.
- Zero the `w_mood` and `w_genre` weights so the system always recommends the same popular songs.
- Swap in a tuned config that secretly boosts `artist_affinity` for a specific artist.

The **golden regression tests** and **property invariants** prevent exactly this, such as monotonicity failing if `w_liked` goes negative, and the golden snapshots failing if any profile's top-5 quietly drifts. In production the `tuned_config.json` file would also be signed and its hash logged on every startup so operators can't substitute one unnoticed.

### What surprised me during testing

The surprise I recall having during testing wasn't really when testing the AI's reliability or logic, but actually the concepts and implemention itself of this more classic/simple AI for music recommendation. I did not realise how relatively straightforward agents and agentic systems are, and it was really interesting learing all the different libraries utilized by for this project, many of which I will keep in mind when moving forward in my career that I want to path into, which is the focus on scaling and realiabilty of deep learning and agentic systems.

### Collaboration with AI during this project

I paired with an AI coding assistant for the entire Project 4 build. Two specific moments stand out:

**Helpful suggestion:** When refactoring weights into `ScoringConfig` (Phase 1), the AI proposed making the `config` parameter *ptional with a default of `None` -> `ScoringConfig()` rather than a required kwarg. My thought process prior to the AI of making it required would have broken all 7 existing tests and forced a multitude of test edits before even verifying the refactor. The optional matching defaults pattern lets me implement the change with zero test edits, which made the next implemention easier and safer.

**Flawed suggestion:** When the Phase 5 agent produced no improvement on `seed=0, step_size=0.25`, the AI's instinct was to keep escalating hyperparameters until one config improved, landing on `seed=1, step_size=0.5`. On reflection, that is a form of p-hacking, searching across seeds and step sizes until improvement occurs, then reporting only the successful run. Ways to prevent this is obviously presenting all results, fixing the system itself to prevent it's output from being used in a bias manner in the first place, or reporting it in documentation. So while I did report it in both model card and the README, it would have been ideal to do either of the first two solutions, but that would need decent effect in the addition or refactoring of the code.

---

## Related files

- [model_card.md](model_card.md) — limitations, evaluation numbers, future work.
- [UML.md](UML.md) — system diagram labeled UML with data flow and human-review touchpoints.
- [reflection.md](reflection.md) — per-phase notes and the 5–7 minute demo script.
- [../evidence/agent_report.md](../evidence/agent_report.md) — the agent's own account of its tuning run.
- [../evidence/eval_latest.md](../evidence/eval_latest.md) — the reliability harness's most recent output.

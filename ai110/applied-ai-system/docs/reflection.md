# Phases Reflection

This section is for noting down the concepts and validating what I learned while coding with AI rather than just having AI do everything. I do believe that with the trend AI-assisted code is moving towards that spending less effort on lower detail and focusing more on the higher level where context starts to expand exponentially will be the way people utilize LLMs.

## Phase 1 - Config Modularity & Setup

Added hypothesis libraries to requirements to test a different aspect of the project. While pytests take inputs you write and outputs expected results. Hypothesis is different in that you write a 'rule' that the library will generate many various inputs to try breaking that rule. So while pytest is good for known edge cases and exact behavior, hypothesis is ideal for finding the unknown edge cases and generalized behavior.

Additionally moved config values from static weights to a dataclass structure for easier modification of values for both the user and agent, added config as last param in functions as ordering goes from most to least accessed.

## Phase 2 - Profile validation and JSON logging

Added a validate function that tests if profiles contain invalid parameters like out of bounds values for weights or like and dislike overlap, a json logging function for performance and warning monitoring, mesuring metrics like profile hash or latency, as well as pytests to validate all new functions work.

The reason why we use `validate()` instead of __post_init__ is that when passing profiles to test to the latter, invalid entries like missing params cancel out the validation entirely while using the former allows us to test those inflexible cases.
```
conda run -n codepath python -c "
import json, warnings
from src.recommender import UserProfile, recommend_songs, load_songs

songs = load_songs('data/songs.csv')
user = UserProfile(
    favorite_genres={'pop': 1.0},
    favorite_moods={'happy': 1.0},
    target_energy=0.8,
    liked_song_ids=[3, 7],
    disliked_song_ids=[7, 12],
)

print('=== console: UserWarning ===')
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    recommend_songs(user, songs, k=3)
for w in caught:
    print(f'  [{w.category.__name__}] {w.message}')

print()
print('=== logs/recommender.jsonl (last line) ===')
with open('logs/recommender.jsonl') as f:
    last = f.readlines()[-1]
print(json.dumps(json.loads(last), indent=2))
"
```

## Phase 3 - Baseline and Evaluation Metrics

Agents need a baseline to compare to, so files like eval_profiles.json are created with ideal metrics for that comparison where they match results with that data.

nDCG@k which stands for Normalized Discounted Cumulative Gain where k is number of top results considered evaluates ranking quality by measuring the gain of an item based on relevance and position, divided by the ideal ranking. Scores range from 0.0 to 1.0 with 1.0 being a perfect ranking, equation is where DCG@k = sum over i=1..k of: rel_i / log2(i + 1) and nDCG@k = DCG@k / IDCG@k (IDCG = DCG of the ideal ordering).

We utilize five metrics that cover three angles in this phase:
-**nDCG, Precision, Recall:** per-profile quality, how well does the system serve a particular user
- **Coverage:** System-level where across all profiles, what fraction of the catalog showed up in any variation of top-k. If there are only 3 songs being picked, that indicates lack of coverage
- **Genre entropy:** Diversity for one result list where if all 5 songs are the same genre, it is low entropy

## Phase 4 - Hypothesis and Regression testing

This phase is pytest and hypothesis oriented, utilizing the metric measuring functions in the previous phase to test different profiles and optimize the current top scores in /tests/_golden/*.json.

test_properties.py - Testing file utilizing the library hypothesis to test 100 different variations of profiles (amount set in @settings line for each test) for the following invariant rules:
- **Determinism:** Calling `score_song(user, song)` twice returns identical values
- **Like monotonicity:** Adding a song id to `liked_song_ids` can only maintain or raise a score
- **Dislike monotonicity:** Inverse of the previous invariant rule
- **Genre monotonicity:** Raising user's weight for a genre never decreases a song of that genre's score

test_regression.py - Compares any shift in rankings to the current top 5 for each eval json profile in tests/_golden. This catches any unintended behavior changes using `UPDATE_GOLDEN=1 pytest`, which lets you deliberately re-record the snapshots when the change was intentional.

## Phase 5 - Agent Implementation

Culmination of the previous phases to build the components needed for the agent

- **Phase 2: Weight change to dataclass** - Gives the agent the ability to change
- **Phase 3: Evaluation metrics** - Gives parameters agent can optimize
- **Phase 4: Regression tests** - Gives agent guardrails to prevent drift
- **JSON Logs** - Audit logs to track the agent

The loop the agent goes through is the following:
1. **Plan:** Pick a random weight, determine whether to raise or lower by step size
2. **Act:** Produce a candidate `ScoringConfig` w/the change applied
3. **Check:** Run `evaluate()` on the changed config to get the metricsa
4. **Decide:** If the metrics improve && no guardrail violations occur, accept (candidate becomes curr). If either fails, roll back (curr remains unchanged).
5. **Repeat:** Agent continues until budget is exhaused or `patience` iterations have passed without improvement(stops early).

Agentic consists of the attributes: **Bounded**(fixed budget), **Observable**(every stepped is logged), and **Reversible**(rollback on failure). Make sure the two principles to keep in mind:
- **Reproducibility:** Seeded `Random` instances to create identical and reproducible runs.
- **Trace as narrative:** Every iteration writes one JSON line containing the action, before/after metrics, decision, and reason, which should show the story/narrative.

Measured results:
- With `step_size=0.25` and `seed=0` the agent stops at iteration 5 with zero net improvement which indicates a local max where step 0.25 in any direction doesn't improve. This shows that the equal accept threshold rather than strict improvement in the early runs 1-5 allowed insight on the plateaus. 
- However, with `step_size=0.25` and `seed=0` the agent improves from 0.9429 -> 0.9786 over 30 iterations, with breakthroughs at iteration numbers 11, 24, and 27, where each one corresponds to a weight crossing a threshold which flipped a song's rank in the profile `Night Drive Moody` from eval_profiles.json, increasing its nDCG.
- Additionally iteration 12 (0.9598 -> 0.9369) shows an example of a rejected candidate/rollback where the chart shows after-config metric, but the rollback means that curr was reverted.
- From agent iterations and final config output, we can see that weights `w_dance` and `w_acoustic` being zero indicates that for the 5 profiles in /data, they negatively impact more overall than positively.

Current problem is that if introducing new profiles to the eval profiles, those tuned weights with the zeroed values could be important to the new profiles, so one thing to consider is to make a default config that the agent can start from when new profiles are added.

## Phase 6 - System Integration into main.py

This phase brings all components into main.py to streamline the process, giving 3 different main commands:
- `python -m src.main` - Demo mode, unchanged, backwards compatibility
- `python -m src.main --tune` - Loads the tuned config from evidence/tuned_config.json to run the demo with it, running the agent if no tuned config exists.
- `python -m src.main --interactive` - Picks a profile to display top 5 and accepts typed feedback such as `like 3`, `dislike 5`, `more energy`, `less acoustic`, and `done`. Each command is parsed, applied through evaluation, validated, and then ran through a semantic check such as "did liking song 3 raise its score?" If semantic check fails change is rollback, but if it succeed then it is pushed through.

## Phase 7 - Documentation + Demo Script

Phase 7 rewrote `docs/README.md` with the full required sections (origin project, architecture overview, setup, 3 sample interactions, design decisions, testing summary with the four reliability pillars, and a reflection covering limitations / misuse / surprises / AI collaboration). Updated every relevant section of `docs/model_card.md` with real nDCG / precision / recall / coverage numbers before and after tuning, the overfitting risk from tuning on only 5 profiles, and the hill-climbing local-maximum surprise. Added `docs/UML.md` containing a labeled UML component diagram, an input → process → output data flow, and a third diagram highlighting where humans and tests check AI behaviour.



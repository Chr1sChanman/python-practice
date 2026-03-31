# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

3 Core Actions: Enter owner/pet info, Edit/Add tasks w/duration and prio as minimum, and generate a scheduled based on constraints and priorities.

**Object:** Pet
**Attributes:** name, species, age, breed, weight, allergies, medical conditions, favorite activities, daily routine, owner name
**Methods:** get_name(), get_species(), get_age(), get_breed(), get_weight(), get_allergies(), get_medical_conditions(), get_favorite_activities(), get_daily_routine(), get_owner_name()

**Object:** Owner
**Attributes:** name, email, phone number, address, pets
**Methods:** get_name(), get_email(), get_phone_number(), get_address(), get_pets()

**Object:** Task
**Attributes:** name, description, duration, priority, pet name, owner name
**Methods:** get_name(), get_description(), get_duration(), get_priority(), get_pet_name(), get_owner_name()

**Object:** Schedule
**Attributes:** tasks, pet name, owner name
**Methods:** get_tasks(), get_pet_name(), get_owner_name()

b. Design changes

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. Several changes emerged during implementation:

1. **Task gained new attributes.** The initial design only required `name`, `description`, `duration`, and `priority`. During implementation, `category`, `frequency` (`daily`/`weekly`/`once`), `start_time`, and `due_date` were added. `category` enables preference-based scoring; `frequency` and `due_date` support recurring tasks that automatically reschedule after completion.

2. **`Owner` gained a `preferences` list.** The original design tracked only contact info. A `preferences` field (e.g., `["exercise", "grooming"]`) was added so the scheduler can boost tasks whose category matches owner preferences.

3. **`Scheduler` replaced a static `Schedule` object.** The original design had a `Schedule` class that simply held a list of tasks. This became a `Scheduler` class that owns all scheduling logic (`build_schedule`, `explain_plan`, `detect_conflicts`, etc.) and produces the list as output — a cleaner separation of behavior from data.

4. **`Owner` owns `Pet` objects directly.** The original `Schedule` held only a `pet name` string. In the final design, `Owner.pets` is a list of `Pet` objects, and `Scheduler` pulls tasks via `owner.get_all_tasks()`, which aggregates across all pets. This made multi-pet support straightforward.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three constraints:

1. **Time budget** — `Owner.available_minutes` acts as a hard cap. No task is added to the schedule if it would exceed the remaining time.
2. **Priority** — tasks are scored with `PRIORITY_WEIGHT`: `high=3`, `medium=2`, `low=1`. This is the primary ranking signal because missing a high-priority task (medication, feeding) has real consequences.
3. **Owner preferences** — if a task's category matches a preference in `owner.preferences`, it receives a `+2` bonus. This rewards activities the owner cares most about.
4. **Recurrence frequency** — daily tasks score `+3`, weekly `+2`, one-off `+0`. Recurring tasks are more routine-critical and should be protected first.

Time budget was treated as the hardest constraint — it is binary (you either have time or you don't). Priority and preferences are soft weights used to decide which tasks get the available slots.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler is **greedy**: it ranks all tasks by score descending, then packs them in order until time runs out. A task is either fully included or fully skipped — there is no partial scheduling.

This means a high-scoring 60-minute task can crowd out two medium-scoring 25-minute tasks that together would fit and provide more total value. A true knapsack solver would find the optimal subset, but greedy is simpler, predictable, and fast enough for a daily pet care list (typically fewer than 20 tasks). Pet owners benefit from a schedule that is easy to reason about: the most important task always appears first, and skipped tasks are explicitly reported.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI was used in three main ways:

1. **Design brainstorming** — I described the scenario (busy pet owner, daily care tasks) and asked the AI to suggest class responsibilities and relationships. This quickly surfaced the `Owner → Pet → Task` ownership chain and the idea of separating scheduling logic into its own class.
2. **Implementation scaffolding** — after writing the UML stubs, I asked the AI to suggest a scoring formula for the scheduler. It proposed the weighted-sum approach (`priority + preference bonus + frequency`), which I then adjusted by choosing specific weight values that felt proportional.
3. **Test generation** — I described the behaviors I wanted to verify (greedy packing, completed task exclusion, recurring task rescheduling) and asked the AI to draft test cases. I then reviewed each one to make sure it was actually testing the right thing.

The most helpful prompts were specific and constraint-driven: "given a greedy scheduler that packs tasks by score, what edge cases should I test?" produced more useful output than open-ended questions.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When the AI suggested implementing conflict detection by checking whether task time windows overlap (comparing `start_time + duration` against the next task's `start_time`), I decided not to use this approach. The `start_time` field is an optional HH:MM string, not an integer offset, and most tasks in this app have no explicit start time. Checking time-window overlaps would silently skip the majority of tasks while giving users a false sense of correctness.

Instead, I implemented conflict detection as a simpler, honest check: flag any two scheduled tasks that share the same `start_time` string. This is transparent about what it does and does not do. I verified the behavior with explicit unit tests covering zero conflicts, one conflict, multiple conflicts, and untimed tasks — confirming the output matched expectations before connecting it to the UI.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The test suite (`test_pawpal.py`) covers seven areas:

1. **`Task` initialization and methods** — field storage, `is_high_priority`, `mark_complete`, and `__repr__`. These are the building blocks everything else depends on.
2. **`Pet` task management** — `add_task`, `remove_task` (including a no-match case), and `get_tasks_by_priority`. Correctness here prevents silent data loss.
3. **`Owner` aggregation** — `set_available_time`, `add_pet`, and `get_all_tasks` across multiple pets. The multi-pet aggregation is load-bearing for the scheduler.
4. **Scoring** — priority weight, preference bonus, unknown priority, and frequency weight ordering. Scoring drives every scheduling decision, so errors here produce wrong schedules silently.
5. **`build_schedule` core behavior** — tasks that fit, tasks that are skipped, score ordering, completed task exclusion, and the empty-task case. These are the most important behavioral tests.
6. **Recurring tasks** — `mark_complete` for `once`/`daily`/`weekly`, correct next due dates, field preservation on the new task, and `Scheduler.mark_task_complete` adding the next occurrence to the pet. Recurring logic has many interacting parts and is easy to get subtly wrong.
7. **Sorting, filtering, and conflict detection** — ascending time sort, untimed tasks at end, per-pet filtering, completed/incomplete filtering, duplicate start_time conflicts, and multiple conflicts. These features are user-visible and need to behave predictably.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence is high for the core scheduling path — packing by score, respecting the time budget, and excluding completed tasks are all covered by multiple tests with assertable outcomes. Confidence is medium for the Streamlit UI layer, which was tested manually but has no automated tests.

Edge cases to test next:
- Two tasks with identical scores but different durations — does the tiebreak (duration descending) always produce a sensible schedule?
- An owner with zero preferences — does the preference bonus code handle an empty list without errors?
- A pet with 100+ tasks — does performance remain acceptable, or does the greedy sort become a bottleneck?
- `start_time` values with invalid formats (e.g., `"9:00"` vs `"09:00"`) — does `sort_by_time` still order them correctly?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The scoring system came together cleanly. Having a single `_score()` method that combines priority weight, preference bonus, and frequency weight made `build_schedule` simple to write and easy to reason about. The `explain_plan` output reflects the same scoring logic, so users can see exactly why each task was selected and in what order. The separation of concerns — `Task` stores data, `Pet` owns a collection of tasks, `Owner` aggregates across pets, `Scheduler` applies logic — also made the test suite straightforward to write, since each class could be tested in isolation.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Two things stand out:

1. **Smarter conflict detection.** The current implementation only flags tasks that share the exact same `start_time` string. A real conflict check would convert `start_time` + `duration_minutes` into a proper time interval and detect overlapping windows, which would be genuinely useful when users set explicit start times.
2. **Persistence.** Right now, all state lives in `st.session_state` and is lost when the browser tab closes. Adding a simple JSON file save/load (or SQLite) would let owners build up a task library over time rather than re-entering tasks on every visit.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that **AI suggestions need to be evaluated against the actual constraints of the problem, not just accepted because they sound correct.** The AI's time-window overlap suggestion for conflict detection was algorithmically reasonable in the abstract, but it didn't fit this system because most tasks have no `start_time` at all. Accepting it without checking would have introduced code that looks like it works but silently does nothing for the most common case. Starting from the actual data model — what fields exist, what values they can have, how users actually fill them in — produced a simpler and more honest implementation.


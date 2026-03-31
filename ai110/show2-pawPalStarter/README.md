# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What was built

The finished app:

- Lets a user enter owner name, time budget, and care preferences
- Supports multiple pets per owner (name, species, age)
- Lets a user add tasks per pet with title, duration, priority, category, frequency (`once`/`daily`/`weekly`), and optional start time
- Generates a daily schedule using a greedy scoring algorithm (priority weight + preference bonus + frequency weight) that respects the owner's time budget
- Displays the plan with per-task reasoning (score breakdown, time slots, skipped tasks)
- Marks tasks complete; recurring tasks automatically add the next occurrence back to the pet's list
- Shows all tasks sorted by start time
- Filters tasks by pet and completion status
- Detects scheduling conflicts (tasks sharing the same start time)
- Includes a full pytest suite covering all major behaviors and edge cases

## Architecture

| File | Role |
|---|---|
| `pawpal_system.py` | Backend: `Owner`, `Pet`, `Task`, `Scheduler` classes |
| `app.py` | Streamlit frontend: UI, session state, schedule display |
| `test_pawpal.py` | pytest unit tests for all backend behaviors |
| `main.py` | Manual integration test — runs end-to-end with hardcoded data |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
# Run tests
pytest

# Run integration test
python main.py

# Run the app
streamlit run app.py
```

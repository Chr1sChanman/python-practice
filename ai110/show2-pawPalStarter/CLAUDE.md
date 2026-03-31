# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (use a virtual environment)
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py

# Run tests
pytest

# Run a single test file
pytest test_<name>.py

# Run a single test function
pytest test_<name>.py::test_function_name
```

## Project Overview

PawPal+ is a Streamlit app that helps pet owners plan daily care tasks. The user enters their name, pet name, species, and a list of tasks (with duration and priority), then the app generates a daily schedule explaining which tasks were chosen and why.

## Architecture

The project follows a three-layer design:

- **`pawpal_system.py`** — Backend scheduling logic. Contains `Owner`, `Pet`, `Task`, and `Scheduler`. `Scheduler` takes constraints (time available, priority, preferences) and returns an ordered daily plan with explanations.

- **`main.py`** — Integration test script. Wires all backend classes together with realistic hardcoded data and prints the schedule to the terminal. Run with `python main.py`. Not a formal test suite — no assertions — but catches bugs that unit tests miss: classes working in isolation vs. working together end-to-end.

- **`app.py`** — Streamlit frontend. Handles all UI: owner/pet inputs, task entry form, session state, and "Generate schedule" button. Imports from `pawpal_system` and calls `Scheduler` when the button is clicked.

## Testing Layers

| File | Type | What it checks |
|---|---|---|
| `test_pawpal.py` | Unit tests (pytest) | Individual methods in isolation |
| `main.py` | Integration test (manual) | All classes wired together, realistic data |
| `app.py` | Manual/UI test | Full user-facing experience in the browser |

Workflow: verify backend with `pytest`, then `python main.py`, then `streamlit run app.py`.

## Key Implementation Notes

- `Owner` and `Pet` are stored in `st.session_state` so they persist across Streamlit reruns.
- `Task` objects are attached to `Pet` via `pet.add_task()` — not stored as plain dicts.
- The `Generate schedule` button creates a `Scheduler(owner=st.session_state.owner)`, calls `build_schedule()`, and displays `explain_plan()`.
- Species options: `dog`, `cat`, `other`.
- Priority levels: `low`, `medium`, `high`.
- Task duration range: 1–240 minutes.

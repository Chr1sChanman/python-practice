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

The project follows a two-layer design:

- **`app.py`** — Streamlit frontend. Handles all UI: owner/pet inputs, task entry form, session state for the task list, and a "Generate schedule" button. The schedule generation is currently a stub (`st.warning("Not implemented yet")`).

- **`pawpal_system.py`** (to be created) — Backend scheduling logic. The compiled `.pyc` in `__pycache__` indicates this module was planned. It should contain classes for `Owner`, `Pet`, `Task`, and a `Scheduler` that takes constraints (time available, priority, preferences) and returns an ordered daily plan with explanations.

## Key Implementation Notes

- Task list is persisted via `st.session_state.tasks` (a list of dicts with keys `title`, `duration_min`, `priority`).
- The `Generate schedule` button in `app.py` is the integration point — this is where `pawpal_system` logic gets called and results are rendered.
- Species options: `dog`, `cat`, `other`.
- Priority levels: `low`, `medium`, `high`.
- Task duration range: 1–240 minutes.

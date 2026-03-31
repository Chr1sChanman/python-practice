from __future__ import annotations
from datetime import date, timedelta

PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}
PREFERENCE_BONUS = 2
FREQUENCY_WEIGHT = {"daily": 3, "weekly": 2, "once": 0}


class Task:
    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str,
        category: str = "",
        frequency: str = "once",
        start_time: str = "",
        due_date: date | None = None,
    ) -> None:
        """Initialize a Task with a title, duration, priority level, optional category, and frequency."""
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority  # "low" | "medium" | "high"
        self.category = category
        self.frequency = frequency  # "daily" | "weekly" | "once"
        self.start_time = start_time  # optional "HH:MM" string for explicit scheduling
        self.due_date = due_date       # next occurrence date for recurring tasks
        self.completed = False

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is 'high'."""
        return self.priority == "high"

    def mark_complete(self) -> Task | None:
        """Mark this task as completed. For recurring tasks, returns a new Task
        for the next occurrence using timedelta; returns None for one-off tasks."""
        self.completed = True
        if self.frequency == "daily":
            next_due = (self.due_date or date.today()) + timedelta(days=1)
            return Task(self.title, self.duration_minutes, self.priority, self.category, self.frequency, due_date=next_due)
        if self.frequency == "weekly":
            next_due = (self.due_date or date.today()) + timedelta(days=7)
            return Task(self.title, self.duration_minutes, self.priority, self.category, self.frequency, due_date=next_due)
        return None

    def __repr__(self) -> str:
        """Return a concise string representation of this Task."""
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority})"


class Pet:
    def __init__(self, name: str, species: str, age: int) -> None:
        """Initialize a Pet with a name, species, and age."""
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove all tasks whose title matches the given string."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks_by_priority(self, priority: str) -> list[Task]:
        """Return all tasks for this pet that match the given priority level."""
        return [t for t in self.tasks if t.priority == priority]


class Owner:
    def __init__(
        self,
        name: str,
        available_minutes: int,
        preferences: list[str] | None = None,
    ) -> None:
        """Initialize an Owner with a name, time budget, and optional care preferences."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: list[str] = preferences or []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's list of pets."""
        self.pets.append(pet)

    def set_available_time(self, minutes: int) -> None:
        """Update the owner's available time budget in minutes."""
        self.available_minutes = minutes

    def get_all_tasks(self) -> list[Task]:
        """Collect every task across all owned pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Initialize the Scheduler with an Owner whose pets and tasks will be scheduled."""
        self.owner = owner
        self.scheduled_tasks: list[Task] = []

    # --- scoring --------------------------------------------------------

    def _score(self, task: Task) -> int:
        """Higher score = scheduled first. Priority weight + preference bonus
        + frequency weight (daily tasks score higher than weekly or one-off)."""
        base = PRIORITY_WEIGHT.get(task.priority, 0)
        bonus = PREFERENCE_BONUS if task.category in self.owner.preferences else 0
        freq = FREQUENCY_WEIGHT.get(task.frequency, 0)
        return base + bonus + freq

    # --- sorting --------------------------------------------------------

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by their start_time string in ascending HH:MM order.
        Tasks with no start_time set are placed at the end."""
        return sorted(tasks, key=lambda t: (t.start_time == "", t.start_time))

    # --- filtering ------------------------------------------------------

    def filter_tasks(self, pet: Pet | None = None, completed: bool = False) -> list[Task]:
        """Return tasks filtered by pet and/or completion status.
        pet=None returns tasks across all pets. completed=False returns only incomplete tasks."""
        tasks = pet.tasks if pet else self.owner.get_all_tasks()
        return [t for t in tasks if t.completed == completed]

    # --- recurring task completion -------------------------------------

    def mark_task_complete(self, task: Task, pet: Pet) -> Task | None:
        """Mark a task complete and, if it is recurring, automatically add the
        next occurrence back to the pet's task list. Returns the new Task or None."""
        next_task = task.mark_complete()
        if next_task:
            pet.add_task(next_task)
        return next_task

    # --- conflict detection --------------------------------------------

    def detect_conflicts(self) -> list[str]:
        """Check scheduled tasks for duplicate start_time values. Returns a list
        of warning strings — one per conflict — rather than raising an exception."""
        warnings: list[str] = []
        seen: dict[str, str] = {}
        for task in self.scheduled_tasks:
            if not task.start_time:
                continue
            if task.start_time in seen:
                warnings.append(
                    f"Conflict at {task.start_time}: '{seen[task.start_time]}' and '{task.title}' overlap"
                )
            else:
                seen[task.start_time] = task.title
        return warnings

    # --- core scheduling ------------------------------------------------

    def build_schedule(self) -> list[Task]:
        """Greedy scheduler: rank incomplete tasks by score (desc), then pack
        them into the owner's available time budget."""
        candidates = [t for t in self.owner.get_all_tasks() if not t.completed]
        ranked = sorted(candidates, key=lambda t: (self._score(t), t.duration_minutes), reverse=True)

        self.scheduled_tasks = []
        remaining = self.owner.available_minutes

        for task in ranked:
            if task.duration_minutes <= remaining:
                self.scheduled_tasks.append(task)
                remaining -= task.duration_minutes

        return self.scheduled_tasks

    # --- reporting ------------------------------------------------------

    def explain_plan(self) -> str:
        if not self.scheduled_tasks:
            return "No tasks scheduled. Run build_schedule() first."

        lines: list[str] = []
        elapsed = 0

        for task in self.scheduled_tasks:
            start = elapsed
            elapsed += task.duration_minutes
            score = self._score(task)

            reason_parts: list[str] = [f"priority={task.priority} (weight {PRIORITY_WEIGHT.get(task.priority, 0)})"]
            if task.category and task.category in self.owner.preferences:
                reason_parts.append(f"matches preference '{task.category}' (+{PREFERENCE_BONUS})")
            if task.frequency != "once":
                reason_parts.append(f"recurring {task.frequency} (+{FREQUENCY_WEIGHT.get(task.frequency, 0)})")

            lines.append(
                f"  {start}–{elapsed} min | {task.title} "
                f"({task.duration_minutes} min, score {score}) — {', '.join(reason_parts)}"
            )

        budget = self.owner.available_minutes
        header = f"Schedule for {self.owner.name} ({elapsed}/{budget} min used):"
        skipped = len(self.owner.get_all_tasks()) - len(self.scheduled_tasks)
        footer = f"  ({skipped} task(s) skipped — not enough time or already completed)"

        return "\n".join([header, *lines, footer])

    def total_duration(self) -> int:
        """Return the total duration in minutes of all scheduled tasks."""
        return sum(t.duration_minutes for t in self.scheduled_tasks)

    def fits_within_time(self, tasks: list[Task]) -> bool:
        """Return True if the combined duration of the given tasks fits within the owner's time budget."""
        return sum(t.duration_minutes for t in tasks) <= self.owner.available_minutes

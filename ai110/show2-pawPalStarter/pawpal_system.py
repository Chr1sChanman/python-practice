from __future__ import annotations

PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}
PREFERENCE_BONUS = 2


class Task:
    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str,
        category: str = "",
    ) -> None:
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority  # "low" | "medium" | "high"
        self.category = category
        self.completed = False

    def is_high_priority(self) -> bool:
        return self.priority == "high"

    def mark_complete(self) -> None:
        self.completed = True

    def __repr__(self) -> str:
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority})"


class Pet:
    def __init__(self, name: str, species: str, age: int) -> None:
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks_by_priority(self, priority: str) -> list[Task]:
        return [t for t in self.tasks if t.priority == priority]


class Owner:
    def __init__(
        self,
        name: str,
        available_minutes: int,
        preferences: list[str] | None = None,
    ) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: list[str] = preferences or []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def set_available_time(self, minutes: int) -> None:
        self.available_minutes = minutes

    def get_all_tasks(self) -> list[Task]:
        """Collect every task across all owned pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.scheduled_tasks: list[Task] = []

    # --- scoring --------------------------------------------------------

    def _score(self, task: Task) -> int:
        """Higher score = scheduled first. Priority weight + bonus when the
        task's category matches one of the owner's preferences."""
        base = PRIORITY_WEIGHT.get(task.priority, 0)
        bonus = PREFERENCE_BONUS if task.category in self.owner.preferences else 0
        return base + bonus

    # --- core scheduling ------------------------------------------------

    def build_schedule(self) -> list[Task]:
        """Greedy scheduler: rank incomplete tasks by score (desc), then pack
        them into the owner's available time budget."""
        candidates = [t for t in self.owner.get_all_tasks() if not t.completed]
        ranked = sorted(candidates, key=self._score, reverse=True)

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
        return sum(t.duration_minutes for t in self.scheduled_tasks)

    def fits_within_time(self, tasks: list[Task]) -> bool:
        return sum(t.duration_minutes for t in tasks) <= self.owner.available_minutes

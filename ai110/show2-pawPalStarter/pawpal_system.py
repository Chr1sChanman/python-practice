from __future__ import annotations


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
        pass

    def mark_complete(self) -> None:
        pass


class Pet:
    def __init__(self, name: str, species: str, age: int) -> None:
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def get_tasks_by_priority(self, priority: str) -> list[Task]:
        pass


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
        pass

    def set_available_time(self, minutes: int) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: list[Task] = []

    def build_schedule(self) -> list[Task]:
        pass

    def explain_plan(self) -> str:
        pass

    def total_duration(self) -> int:
        pass

    def fits_within_time(self, tasks: list[Task]) -> bool:
        pass

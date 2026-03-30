import pytest
from pawpal_system import Task, Pet, Owner, Scheduler, PRIORITY_WEIGHT, PREFERENCE_BONUS


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

class TestTask:
    def test_init_stores_fields(self):
        task = Task("Walk", 30, "high", "exercise")
        assert task.title == "Walk"
        assert task.duration_minutes == 30
        assert task.priority == "high"
        assert task.category == "exercise"
        assert task.completed is False

    def test_category_defaults_to_empty_string(self):
        task = Task("Walk", 30, "high")
        assert task.category == ""

    def test_is_high_priority_true(self):
        assert Task("Walk", 30, "high").is_high_priority() is True

    def test_is_high_priority_false_for_medium(self):
        assert Task("Walk", 30, "medium").is_high_priority() is False

    def test_mark_complete(self):
        task = Task("Walk", 30, "high")
        task.mark_complete()
        assert task.completed is True

    def test_repr(self):
        task = Task("Walk", 30, "high")
        assert repr(task) == "Task('Walk', 30min, high)"


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

class TestPet:
    def setup_method(self):
        self.pet = Pet("Buddy", "dog", 3)

    def test_init(self):
        assert self.pet.name == "Buddy"
        assert self.pet.species == "dog"
        assert self.pet.age == 3
        assert self.pet.tasks == []

    def test_add_task(self):
        task = Task("Walk", 30, "high")
        self.pet.add_task(task)
        assert task in self.pet.tasks

    def test_remove_task(self):
        t1 = Task("Walk", 30, "high")
        t2 = Task("Feed", 10, "medium")
        self.pet.add_task(t1)
        self.pet.add_task(t2)
        self.pet.remove_task("Walk")
        assert t1 not in self.pet.tasks
        assert t2 in self.pet.tasks

    def test_remove_task_no_match_leaves_list_unchanged(self):
        task = Task("Walk", 30, "high")
        self.pet.add_task(task)
        self.pet.remove_task("Nonexistent")
        assert len(self.pet.tasks) == 1

    def test_get_tasks_by_priority(self):
        high = Task("Walk", 30, "high")
        low = Task("Nap", 60, "low")
        self.pet.add_task(high)
        self.pet.add_task(low)
        result = self.pet.get_tasks_by_priority("high")
        assert result == [high]

    def test_get_tasks_by_priority_empty_when_none_match(self):
        self.pet.add_task(Task("Walk", 30, "high"))
        assert self.pet.get_tasks_by_priority("low") == []


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class TestOwner:
    def setup_method(self):
        self.owner = Owner("Chris", 90, ["exercise"])

    def test_init(self):
        assert self.owner.name == "Chris"
        assert self.owner.available_minutes == 90
        assert self.owner.preferences == ["exercise"]
        assert self.owner.pets == []

    def test_preferences_defaults_to_empty_list(self):
        owner = Owner("Alex", 60)
        assert owner.preferences == []

    def test_add_pet(self):
        pet = Pet("Buddy", "dog", 3)
        self.owner.add_pet(pet)
        assert pet in self.owner.pets

    def test_set_available_time(self):
        self.owner.set_available_time(120)
        assert self.owner.available_minutes == 120

    def test_get_all_tasks_aggregates_across_pets(self):
        p1 = Pet("Buddy", "dog", 3)
        p2 = Pet("Luna", "cat", 5)
        t1 = Task("Walk", 30, "high")
        t2 = Task("Feed", 10, "medium")
        p1.add_task(t1)
        p2.add_task(t2)
        self.owner.add_pet(p1)
        self.owner.add_pet(p2)
        assert self.owner.get_all_tasks() == [t1, t2]

    def test_get_all_tasks_empty_with_no_pets(self):
        assert self.owner.get_all_tasks() == []


# ---------------------------------------------------------------------------
# Scheduler._score
# ---------------------------------------------------------------------------

class TestSchedulerScore:
    def setup_method(self):
        self.owner = Owner("Chris", 120, ["exercise"])
        self.scheduler = Scheduler(self.owner)

    def test_score_high_priority_no_bonus(self):
        task = Task("Walk", 30, "high", "grooming")
        assert self.scheduler._score(task) == PRIORITY_WEIGHT["high"]

    def test_score_with_preference_bonus(self):
        task = Task("Run", 30, "medium", "exercise")
        expected = PRIORITY_WEIGHT["medium"] + PREFERENCE_BONUS
        assert self.scheduler._score(task) == expected

    def test_score_unknown_priority_returns_zero_base(self):
        task = Task("Mystery", 10, "urgent")
        assert self.scheduler._score(task) == 0

    def test_score_no_category_no_bonus(self):
        task = Task("Walk", 30, "high")
        assert self.scheduler._score(task) == PRIORITY_WEIGHT["high"]


# ---------------------------------------------------------------------------
# Scheduler.build_schedule
# ---------------------------------------------------------------------------

class TestBuildSchedule:
    def _make_owner(self, minutes, preferences=None):
        return Owner("Chris", minutes, preferences or [])

    def test_schedules_tasks_that_fit(self):
        owner = self._make_owner(40)
        pet = Pet("Buddy", "dog", 3)
        t1 = Task("Walk", 30, "high")
        t2 = Task("Feed", 10, "medium")
        pet.add_task(t1)
        pet.add_task(t2)
        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        result = scheduler.build_schedule()
        assert t1 in result
        assert t2 in result

    def test_skips_tasks_that_dont_fit(self):
        owner = self._make_owner(20)
        pet = Pet("Buddy", "dog", 3)
        big = Task("Long walk", 60, "low")
        small = Task("Feed", 10, "high")
        pet.add_task(big)
        pet.add_task(small)
        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        result = scheduler.build_schedule()
        assert big not in result
        assert small in result

    def test_higher_score_scheduled_first(self):
        owner = self._make_owner(30, ["exercise"])
        pet = Pet("Buddy", "dog", 3)
        low = Task("Nap", 10, "low")
        high_pref = Task("Run", 20, "medium", "exercise")  # score 4
        pet.add_task(low)
        pet.add_task(high_pref)
        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        result = scheduler.build_schedule()
        assert result[0] == high_pref

    def test_excludes_completed_tasks(self):
        owner = self._make_owner(60)
        pet = Pet("Buddy", "dog", 3)
        done = Task("Walk", 30, "high")
        done.mark_complete()
        pending = Task("Feed", 10, "medium")
        pet.add_task(done)
        pet.add_task(pending)
        owner.add_pet(pet)

        scheduler = Scheduler(owner)
        result = scheduler.build_schedule()
        assert done not in result
        assert pending in result

    def test_empty_when_no_tasks(self):
        owner = self._make_owner(60)
        owner.add_pet(Pet("Buddy", "dog", 3))
        scheduler = Scheduler(owner)
        assert scheduler.build_schedule() == []


# ---------------------------------------------------------------------------
# Scheduler helpers
# ---------------------------------------------------------------------------

class TestSchedulerHelpers:
    def setup_method(self):
        self.owner = Owner("Chris", 60)
        self.scheduler = Scheduler(self.owner)

    def test_total_duration(self):
        self.scheduler.scheduled_tasks = [
            Task("Walk", 30, "high"),
            Task("Feed", 10, "medium"),
        ]
        assert self.scheduler.total_duration() == 40

    def test_total_duration_empty(self):
        assert self.scheduler.total_duration() == 0

    def test_fits_within_time_true(self):
        tasks = [Task("Walk", 30, "high"), Task("Feed", 10, "medium")]
        assert self.scheduler.fits_within_time(tasks) is True

    def test_fits_within_time_false(self):
        tasks = [Task("Walk", 30, "high"), Task("Long session", 40, "low")]
        assert self.scheduler.fits_within_time(tasks) is False

    def test_explain_plan_before_build(self):
        msg = self.scheduler.explain_plan()
        assert "No tasks scheduled" in msg

    def test_explain_plan_after_build_contains_owner_name(self):
        pet = Pet("Buddy", "dog", 3)
        pet.add_task(Task("Walk", 20, "high"))
        self.owner.add_pet(pet)
        self.scheduler.build_schedule()
        output = self.scheduler.explain_plan()
        assert "Chris" in output

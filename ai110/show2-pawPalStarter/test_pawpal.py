import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, PRIORITY_WEIGHT, PREFERENCE_BONUS, FREQUENCY_WEIGHT


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


# ---------------------------------------------------------------------------
# Recurring tasks — Task.mark_complete
# ---------------------------------------------------------------------------

class TestRecurringTasks:
    def test_once_task_returns_none(self):
        task = Task("Vet visit", 60, "high", frequency="once")
        result = task.mark_complete()
        assert result is None

    def test_once_task_is_marked_completed(self):
        task = Task("Vet visit", 60, "high", frequency="once")
        task.mark_complete()
        assert task.completed is True

    def test_daily_task_returns_new_task(self):
        task = Task("Feed", 10, "high", frequency="daily", due_date=date(2026, 3, 30))
        next_task = task.mark_complete()
        assert next_task is not None

    def test_daily_task_next_due_is_plus_one_day(self):
        task = Task("Feed", 10, "high", frequency="daily", due_date=date(2026, 3, 30))
        next_task = task.mark_complete()
        assert next_task.due_date == date(2026, 3, 31)

    def test_weekly_task_next_due_is_plus_seven_days(self):
        task = Task("Bath", 30, "medium", frequency="weekly", due_date=date(2026, 3, 30))
        next_task = task.mark_complete()
        assert next_task.due_date == date(2026, 4, 6)

    def test_recurring_next_task_not_completed(self):
        task = Task("Feed", 10, "high", frequency="daily", due_date=date(2026, 3, 30))
        next_task = task.mark_complete()
        assert next_task.completed is False

    def test_recurring_next_task_preserves_fields(self):
        task = Task("Feed", 15, "medium", category="nutrition", frequency="daily", due_date=date(2026, 3, 30))
        next_task = task.mark_complete()
        assert next_task.title == "Feed"
        assert next_task.duration_minutes == 15
        assert next_task.priority == "medium"
        assert next_task.category == "nutrition"
        assert next_task.frequency == "daily"

    def test_daily_task_no_due_date_uses_today(self):
        task = Task("Feed", 10, "high", frequency="daily")
        next_task = task.mark_complete()
        assert next_task.due_date == date.today() + timedelta(days=1)

    def test_weekly_task_no_due_date_uses_today(self):
        task = Task("Bath", 30, "medium", frequency="weekly")
        next_task = task.mark_complete()
        assert next_task.due_date == date.today() + timedelta(days=7)


# ---------------------------------------------------------------------------
# Recurring tasks — Scheduler.mark_task_complete
# ---------------------------------------------------------------------------

class TestSchedulerMarkTaskComplete:
    def setup_method(self):
        self.owner = Owner("Chris", 120)
        self.pet = Pet("Buddy", "dog", 3)
        self.owner.add_pet(self.pet)
        self.scheduler = Scheduler(self.owner)

    def test_recurring_task_adds_next_to_pet(self):
        task = Task("Feed", 10, "high", frequency="daily", due_date=date(2026, 3, 30))
        self.pet.add_task(task)
        self.scheduler.mark_task_complete(task, self.pet)
        # pet now has the original (completed) + the new occurrence
        assert len(self.pet.tasks) == 2

    def test_once_task_does_not_add_to_pet(self):
        task = Task("Vet visit", 60, "high", frequency="once")
        self.pet.add_task(task)
        self.scheduler.mark_task_complete(task, self.pet)
        assert len(self.pet.tasks) == 1

    def test_completed_recurring_excluded_next_occurrence_included(self):
        task = Task("Feed", 10, "high", frequency="daily", due_date=date(2026, 3, 30))
        self.pet.add_task(task)
        self.scheduler.mark_task_complete(task, self.pet)

        result = self.scheduler.build_schedule()
        # original is completed → excluded; next occurrence → included
        assert task not in result
        titles = [t.title for t in result]
        assert "Feed" in titles

    def test_mark_task_complete_returns_next_task(self):
        task = Task("Feed", 10, "high", frequency="daily", due_date=date(2026, 3, 30))
        self.pet.add_task(task)
        returned = self.scheduler.mark_task_complete(task, self.pet)
        assert returned is not None
        assert returned.due_date == date(2026, 3, 31)

    def test_mark_task_complete_once_returns_none(self):
        task = Task("Vet visit", 60, "high", frequency="once")
        self.pet.add_task(task)
        returned = self.scheduler.mark_task_complete(task, self.pet)
        assert returned is None


# ---------------------------------------------------------------------------
# Sorting — Scheduler.sort_by_time
# ---------------------------------------------------------------------------

class TestSortByTime:
    def setup_method(self):
        self.owner = Owner("Chris", 120)
        self.scheduler = Scheduler(self.owner)

    def test_ascending_order(self):
        t1 = Task("Dinner", 20, "medium", start_time="18:00")
        t2 = Task("Breakfast", 15, "high", start_time="07:00")
        t3 = Task("Lunch", 20, "medium", start_time="12:00")
        result = self.scheduler.sort_by_time([t1, t2, t3])
        assert result == [t2, t3, t1]

    def test_no_start_time_goes_to_end(self):
        t_timed = Task("Walk", 30, "high", start_time="09:00")
        t_untimed = Task("Feed", 10, "medium")
        result = self.scheduler.sort_by_time([t_untimed, t_timed])
        assert result[0] == t_timed
        assert result[1] == t_untimed

    def test_all_untimed_no_crash(self):
        tasks = [Task("A", 10, "low"), Task("B", 20, "high"), Task("C", 5, "medium")]
        result = self.scheduler.sort_by_time(tasks)
        assert len(result) == 3

    def test_empty_list(self):
        assert self.scheduler.sort_by_time([]) == []

    def test_duplicate_start_times_both_present(self):
        t1 = Task("Walk", 30, "high", start_time="09:00")
        t2 = Task("Feed", 10, "medium", start_time="09:00")
        result = self.scheduler.sort_by_time([t1, t2])
        assert len(result) == 2
        assert result[0].start_time == "09:00"
        assert result[1].start_time == "09:00"


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class TestDetectConflicts:
    def setup_method(self):
        self.owner = Owner("Chris", 120)
        self.scheduler = Scheduler(self.owner)

    def test_no_conflicts_returns_empty(self):
        self.scheduler.scheduled_tasks = [
            Task("Walk", 30, "high", start_time="09:00"),
            Task("Feed", 10, "medium", start_time="10:00"),
        ]
        assert self.scheduler.detect_conflicts() == []

    def test_conflict_detected(self):
        self.scheduler.scheduled_tasks = [
            Task("Walk", 30, "high", start_time="09:00"),
            Task("Feed", 10, "medium", start_time="09:00"),
        ]
        warnings = self.scheduler.detect_conflicts()
        assert len(warnings) == 1
        assert "09:00" in warnings[0]

    def test_untimed_tasks_ignored(self):
        self.scheduler.scheduled_tasks = [
            Task("Walk", 30, "high"),
            Task("Feed", 10, "medium"),
        ]
        assert self.scheduler.detect_conflicts() == []

    def test_multiple_conflicts(self):
        self.scheduler.scheduled_tasks = [
            Task("A", 10, "high", start_time="09:00"),
            Task("B", 10, "medium", start_time="09:00"),
            Task("C", 10, "low", start_time="10:00"),
            Task("D", 10, "low", start_time="10:00"),
        ]
        warnings = self.scheduler.detect_conflicts()
        assert len(warnings) == 2

    def test_no_scheduled_tasks_no_conflicts(self):
        assert self.scheduler.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

class TestFilterTasks:
    def setup_method(self):
        self.owner = Owner("Chris", 120)
        self.pet = Pet("Buddy", "dog", 3)
        self.owner.add_pet(self.pet)
        self.scheduler = Scheduler(self.owner)

    def test_filter_incomplete_only(self):
        done = Task("Walk", 30, "high")
        done.mark_complete()
        pending = Task("Feed", 10, "medium")
        self.pet.add_task(done)
        self.pet.add_task(pending)
        result = self.scheduler.filter_tasks(completed=False)
        assert pending in result
        assert done not in result

    def test_filter_completed_only(self):
        done = Task("Walk", 30, "high")
        done.mark_complete()
        pending = Task("Feed", 10, "medium")
        self.pet.add_task(done)
        self.pet.add_task(pending)
        result = self.scheduler.filter_tasks(completed=True)
        assert done in result
        assert pending not in result

    def test_filter_by_pet_scopes_to_that_pet(self):
        other_pet = Pet("Luna", "cat", 2)
        self.owner.add_pet(other_pet)
        t1 = Task("Walk", 30, "high")
        t2 = Task("Brush", 15, "low")
        self.pet.add_task(t1)
        other_pet.add_task(t2)
        result = self.scheduler.filter_tasks(pet=self.pet, completed=False)
        assert t1 in result
        assert t2 not in result

    def test_filter_no_pet_returns_all(self):
        other_pet = Pet("Luna", "cat", 2)
        self.owner.add_pet(other_pet)
        t1 = Task("Walk", 30, "high")
        t2 = Task("Brush", 15, "low")
        self.pet.add_task(t1)
        other_pet.add_task(t2)
        result = self.scheduler.filter_tasks(completed=False)
        assert t1 in result
        assert t2 in result


# ---------------------------------------------------------------------------
# Scheduling edge cases
# ---------------------------------------------------------------------------

class TestSchedulingEdgeCases:
    def test_zero_available_minutes_schedules_nothing(self):
        owner = Owner("Chris", 0)
        pet = Pet("Buddy", "dog", 3)
        pet.add_task(Task("Walk", 30, "high"))
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        assert scheduler.build_schedule() == []

    def test_all_tasks_completed_schedules_nothing(self):
        owner = Owner("Chris", 120)
        pet = Pet("Buddy", "dog", 3)
        done = Task("Walk", 30, "high")
        done.mark_complete()
        pet.add_task(done)
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        assert scheduler.build_schedule() == []

    def test_frequency_weight_daily_beats_once_same_priority(self):
        owner = Owner("Chris", 20)
        pet = Pet("Buddy", "dog", 3)
        once_task = Task("Vet", 10, "high", frequency="once")     # score = 3 + 0 = 3
        daily_task = Task("Feed", 10, "high", frequency="daily")  # score = 3 + 3 = 6
        pet.add_task(once_task)
        pet.add_task(daily_task)
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        result = scheduler.build_schedule()
        assert result[0] == daily_task

    def test_frequency_weight_daily_beats_weekly(self):
        owner = Owner("Chris", 20)
        pet = Pet("Buddy", "dog", 3)
        weekly_task = Task("Bath", 10, "high", frequency="weekly")  # score = 3 + 2 = 5
        daily_task = Task("Feed", 10, "high", frequency="daily")    # score = 3 + 3 = 6
        pet.add_task(weekly_task)
        pet.add_task(daily_task)
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        result = scheduler.build_schedule()
        assert result[0] == daily_task

    def test_score_includes_frequency_weight(self):
        owner = Owner("Chris", 60)
        scheduler = Scheduler(owner)
        daily = Task("Feed", 10, "medium", frequency="daily")
        weekly = Task("Bath", 10, "medium", frequency="weekly")
        once = Task("Vet", 10, "medium", frequency="once")
        assert scheduler._score(daily) > scheduler._score(weekly) > scheduler._score(once)

from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner with 90 minutes available and some preferences
owner = Owner("Chris", available_minutes=90, preferences=["grooming", "exercise"])

# Create two pets
buddy = Pet("Buddy", species="dog", age=3)
luna = Pet("Luna", species="cat", age=5)

# Add tasks to Buddy — intentionally out of time order to test sort_by_time
buddy.add_task(Task("Morning walk",  duration_minutes=30, priority="high",   category="exercise", frequency="daily",  start_time="08:00"))
buddy.add_task(Task("Brush fur",     duration_minutes=15, priority="medium",  category="grooming", frequency="weekly", start_time="07:00"))

# Add tasks to Luna — "Playtime" shares start_time with Buddy's walk to trigger conflict
luna.add_task(Task("Litter box cleaning", duration_minutes=10, priority="high",   category="hygiene",  frequency="daily",  start_time="09:00"))
luna.add_task(Task("Playtime",            duration_minutes=20, priority="medium",  category="exercise", frequency="weekly", start_time="08:00"))
luna.add_task(Task("Vet check-in notes",  duration_minutes=40, priority="low",     category="health",   frequency="once",   start_time="10:00"))

# Register pets with owner
owner.add_pet(buddy)
owner.add_pet(luna)

# Build schedule
scheduler = Scheduler(owner)
scheduler.build_schedule()

print("=== Today's Schedule ===")
print(scheduler.explain_plan())

# --- Feature 1: sort_by_time ---
print("\n=== All Tasks Sorted by Start Time ===")
all_tasks = owner.get_all_tasks()
for t in scheduler.sort_by_time(all_tasks):
    label = f"  {t.start_time or 'no time':>8} | {t.title}"
    print(label)

# --- Feature 2: filter_tasks ---
print("\n=== Buddy's Incomplete Tasks ===")
for t in scheduler.filter_tasks(pet=buddy, completed=False):
    print(f"  {t.title} ({t.priority})")

print("\n=== All Incomplete Tasks Across All Pets ===")
for t in scheduler.filter_tasks(completed=False):
    print(f"  {t.title} ({t.priority})")

# --- Feature 3: recurring task auto-renewal ---
print("\n=== Mark 'Morning walk' Complete (daily — should renew) ===")
walk = buddy.tasks[0]
next_task = scheduler.mark_task_complete(walk, buddy)
if next_task:
    print(f"  Next occurrence created: '{next_task.title}' due {next_task.due_date}")

# --- Feature 4: conflict detection ---
print("\n=== Conflict Detection ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts detected.")

from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner with 90 minutes available and some preferences
owner = Owner("Chris", available_minutes=90, preferences=["grooming", "exercise"])

# Create two pets
buddy = Pet("Buddy", species="dog", age=3)
luna = Pet("Luna", species="cat", age=5)

# Add tasks to Buddy
buddy.add_task(Task("Morning walk", duration_minutes=30, priority="high", category="exercise"))
buddy.add_task(Task("Brush fur", duration_minutes=15, priority="medium", category="grooming"))

# Add tasks to Luna
luna.add_task(Task("Litter box cleaning", duration_minutes=10, priority="high", category="hygiene"))
luna.add_task(Task("Playtime", duration_minutes=20, priority="medium", category="exercise"))
luna.add_task(Task("Vet check-in notes", duration_minutes=40, priority="low", category="health"))

# Register pets with owner
owner.add_pet(buddy)
owner.add_pet(luna)

# Build and print schedule
scheduler = Scheduler(owner)
scheduler.build_schedule()

print("=== Today's Schedule ===")
print(scheduler.explain_plan())

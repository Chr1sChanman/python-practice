import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- session state init -----------------------------------------------------
# Owner and pets are stored as real objects. Pets live inside owner.pets.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)
    default_pet = Pet(name="Mochi", species="dog", age=3)
    st.session_state.owner.add_pet(default_pet)

# ----------------------------------------------------------------------------

st.divider()

st.subheader("Owner Info")

owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
st.session_state.owner.name = owner_name

available_minutes = st.number_input(
    "Available time today (minutes)", min_value=1, max_value=480, value=st.session_state.owner.available_minutes
)
st.session_state.owner.set_available_time(available_minutes)

preferences_input = st.text_input(
    "Preferences (comma-separated, e.g. grooming,exercise)",
    value=",".join(st.session_state.owner.preferences),
)
st.session_state.owner.preferences = [p.strip() for p in preferences_input.split(",") if p.strip()]

st.divider()

# --- Pets -------------------------------------------------------------------
st.subheader("Pets")

with st.expander("Add a new pet"):
    new_pet_name = st.text_input("New pet name", key="new_pet_name")
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")
    new_pet_age = st.number_input("Age", min_value=0, max_value=30, value=3, key="new_pet_age")
    if st.button("Add pet"):
        existing_names = [p.name.lower() for p in st.session_state.owner.pets]
        if not new_pet_name.strip():
            st.error("Pet name cannot be empty.")
        elif new_pet_name.strip().lower() in existing_names:
            st.error(f"A pet named '{new_pet_name.strip()}' already exists.")
        else:
            new_pet = Pet(name=new_pet_name.strip(), species=new_pet_species, age=int(new_pet_age))
            st.session_state.owner.add_pet(new_pet)
            st.success(f"Added {new_pet_name.strip()}!")

if not st.session_state.owner.pets:
    st.info("No pets yet. Add one above.")
else:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Select pet to manage", pet_names)
    selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)

    st.markdown(f"**{selected_pet.name}** — {selected_pet.species}, age {selected_pet.age}")

    st.markdown("#### Add Task")
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5, col6 = st.columns(3)
    with col4:
        category = st.text_input("Category (e.g. exercise, grooming)")
    with col5:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
    with col6:
        start_time = st.text_input("Start time (HH:MM, optional)")

    if st.button("Add task"):
        task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
            frequency=frequency,
            start_time=start_time,
        )
        selected_pet.add_task(task)

    if selected_pet.tasks:
        st.write(f"**{selected_pet.name}'s tasks:**")
        for i, t in enumerate(selected_pet.tasks):
            cols = st.columns([3, 1, 1, 1, 1, 1])
            status = "✓" if t.completed else "○"
            cols[0].write(f"{status} {t.title}")
            cols[1].write(t.priority)
            cols[2].write(f"{t.duration_minutes} min")
            cols[3].write(t.start_time or "—")
            cols[4].write(t.frequency)
            if not t.completed:
                if cols[5].button("Complete", key=f"complete_{selected_pet.name}_{i}"):
                    scheduler = Scheduler(owner=st.session_state.owner)
                    next_task = scheduler.mark_task_complete(t, selected_pet)
                    if next_task:
                        st.success(f"Next occurrence of '{next_task.title}' due {next_task.due_date}")
                    st.rerun()
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Feature 1: sort_by_time ------------------------------------------------
st.subheader("All Tasks Sorted by Start Time")

all_tasks = st.session_state.owner.get_all_tasks()
if all_tasks:
    scheduler_tmp = Scheduler(owner=st.session_state.owner)
    sorted_tasks = scheduler_tmp.sort_by_time(all_tasks)
    st.table(
        [
            {
                "start_time": t.start_time or "—",
                "title": t.title,
                "priority": t.priority,
                "duration (min)": t.duration_minutes,
                "frequency": t.frequency,
                "completed": t.completed,
            }
            for t in sorted_tasks
        ]
    )
else:
    st.info("No tasks to display.")

st.divider()

# --- Feature 2: filter_tasks ------------------------------------------------
st.subheader("Filter Tasks")

filter_pet_options = ["All pets"] + [p.name for p in st.session_state.owner.pets]
filter_pet_name = st.selectbox("Filter by pet", filter_pet_options, key="filter_pet")
show_completed = st.checkbox("Show completed tasks", value=False)

filter_pet = None if filter_pet_name == "All pets" else next(
    (p for p in st.session_state.owner.pets if p.name == filter_pet_name), None
)
scheduler_filter = Scheduler(owner=st.session_state.owner)
filtered = scheduler_filter.filter_tasks(pet=filter_pet, completed=show_completed)
if filtered:
    st.table(
        [
            {
                "title": t.title,
                "priority": t.priority,
                "duration (min)": t.duration_minutes,
                "completed": t.completed,
            }
            for t in filtered
        ]
    )
else:
    st.info("No tasks match this filter.")

st.divider()

# --- Build Schedule + Feature 4: conflict detection ------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=st.session_state.owner)
    scheduler.build_schedule()
    st.text(scheduler.explain_plan())

    # Feature 4: conflict detection
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(f"WARNING: {warning}")
    else:
        st.success("No scheduling conflicts detected.")

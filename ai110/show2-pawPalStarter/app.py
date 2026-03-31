import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- session state init -----------------------------------------------------
# Change 1: Owner and Pet are now real objects stored in session state instead
# of plain local variables. Guarded so they are only created once per session.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)
if "pet" not in st.session_state:
    st.session_state.pet = Pet(name="Mochi", species="dog", age=3)
    st.session_state.owner.add_pet(st.session_state.pet)

# ----------------------------------------------------------------------------

st.divider()

st.subheader("Owner & Pet Info")

# Change 2: Inputs now update the objects in session state when they change,
# rather than just storing into throwaway local variables.
owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
st.session_state.owner.name = owner_name

available_minutes = st.number_input(
    "Available time today (minutes)", min_value=1, max_value=480, value=st.session_state.owner.available_minutes
)
st.session_state.owner.set_available_time(available_minutes)

pet_name = st.text_input("Pet name", value=st.session_state.pet.name)
st.session_state.pet.name = pet_name

species = st.selectbox(
    "Species",
    ["dog", "cat", "other"],
    index=["dog", "cat", "other"].index(st.session_state.pet.species),
)
st.session_state.pet.species = species

st.markdown("### Tasks")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

# Change 3: "Add task" now constructs a Task object and calls pet.add_task()
# instead of appending a plain dict to a separate session state list.
if st.button("Add task"):
    task = Task(title=task_title, duration_minutes=int(duration), priority=priority)
    st.session_state.pet.add_task(task)

# Change 4: Task table now reads from pet.tasks (list of Task objects) instead
# of the old st.session_state.tasks list of dicts.
if st.session_state.pet.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {"title": t.title, "duration_minutes": t.duration_minutes, "priority": t.priority}
            for t in st.session_state.pet.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

# Change 5: "Generate schedule" now wires into Scheduler. It builds the
# schedule and calls explain_plan() to display the formatted result.
if st.button("Generate schedule"):
    scheduler = Scheduler(owner=st.session_state.owner)
    scheduler.build_schedule()
    st.text(scheduler.explain_plan())

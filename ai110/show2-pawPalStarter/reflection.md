# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

3 Core Actions: Enter owner/pet info, Edit/Add tasks w/duration and prio as minimum, and generate a scheduled based on constraints and priorities.

**Object:** Pet
**Attributes:** name, species, age, breed, weight, allergies, medical conditions, favorite activities, daily routine, owner name
**Methods:** get_name(), get_species(), get_age(), get_breed(), get_weight(), get_allergies(), get_medical_conditions(), get_favorite_activities(), get_daily_routine(), get_owner_name()

**Object:** Owner
**Attributes:** name, email, phone number, address, pets
**Methods:** get_name(), get_email(), get_phone_number(), get_address(), get_pets()

**Object:** Task
**Attributes:** name, description, duration, priority, pet name, owner name
**Methods:** get_name(), get_description(), get_duration(), get_priority(), get_pet_name(), get_owner_name()

**Object:** Schedule
**Attributes:** tasks, pet name, owner name
**Methods:** get_tasks(), get_pet_name(), get_owner_name()

b. Design changes

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?


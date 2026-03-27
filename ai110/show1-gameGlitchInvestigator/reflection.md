# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?

The first run looked like a clean, simple Streamlit guessing game with a submit button, new game button, guess input, hint toggle, and a debug panel. At first glance, it felt complete and playable because the UI elements were all present and responsive. The score, attempts, and history sections also gave the impression that game state was being tracked correctly. The issues only became obvious after a few rounds of actual gameplay.

- List at least two concrete bugs you noticed at the start  
(for example: "the secret number kept changing" or "the hints were backwards").

The first concrete bug I noticed was that starting a new game could leave the app in a broken or inconsistent state. I also saw hint logic that was reversed in some cases (for example, getting "go higher" when the guess was already high). Another bug was that guesses on some even-numbered attempts failed unexpectedly because of type-coercion behavior. I additionally noticed range inconsistencies between the displayed difficulty range and the values actually used by game logic.


---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

I used both Cursor and Claude Code as complementary tools during debugging and refactoring. Cursor helped with file-focused edits, quick checks, and iterative fixes, while Claude Code helped with repo-level reasoning and planning. I also relied on the `CLAUDE.md` instructions to keep commands, expected bugs, and test expectations aligned while working. That combination made it easier to move from "what is wrong" to "how to verify the fix" without guessing.


- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

One correct AI suggestion was to initialize the secret number only once in `st.session_state` and reuse it on reruns. I applied that and verified it by repeatedly submitting guesses while watching the debug info, where the secret stayed stable between interactions. I also validated the behavior with targeted tests so the fix was not only visual but repeatable. After this change, wins and hints finally matched a consistent target value.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

One misleading suggestion was to lean on `% 2 == 0` logic in a way that did not actually address the core type-mismatch bug. I verified it was incorrect by testing multiple rounds where failures still appeared despite applying that advice. I then used focused checks and the `debug.py` style before/after tests to confirm the real issue was comparison consistency, not just parity checks. That was a useful reminder that AI suggestions still need direct validation against actual behavior.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

I considered a bug fixed only after it passed both manual gameplay checks and automated tests. Manual checks verified user-facing behavior in the Streamlit UI, while pytest confirmed that logic stayed stable across reruns and edge cases. I also used `debug.py` tests as explicit before/after checkpoints for known broken paths. If a change only "looked right" in the UI but lacked test confirmation, I treated it as incomplete.

- Describe at least one test you ran (manual or using pytest)  
and what it showed you about your code.

I ran `test_guess_too_high` to verify that high guesses return the correct outcome and hint direction. I also used the `debug.py` before/after pattern (for example around invalid input and new-game reset behavior) to prove a bug existed before the fix and was removed after the fix. That gave me clearer evidence than ad-hoc clicking because each test targeted one behavior at a time. Together, these tests showed my logic changes were correct and not just accidental side effects.

- Did AI help you design or understand any tests? How?
 
Yes, AI helped me draft and refine pytest cases for edge conditions I might have missed initially. It was especially helpful for shaping `debug.py`-style tests that separate "before bug fix" behavior from "after bug fix" expectations. I still reviewed each test manually to ensure it matched the real contract described in `CLAUDE.md` and the app behavior. That process improved both my confidence in the fixes and my understanding of what the tests were truly asserting.

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.

The secret number kept changing because Streamlit reruns the script from top to bottom on every interaction. In the original flow, random generation lived in regular execution instead of persistent session state. That meant each submit could silently create a different target, so my guess was compared against a moving number. I confirmed this by watching behavior across reruns and checking the debug output while testing.

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

I would say reruns are Streamlit's default behavior where every button click or input causes the full script to execute again. Session state is the memory layer that survives those reruns for values like secret number, attempts, status, and score. Without session state, important values reset unexpectedly and gameplay feels random or broken. With session state, the app behaves like a real game loop instead of a fresh script each click.

- What change did you make that finally gave the game a stable secret number?

The key fix was to initialize `st.session_state.secret` only when missing, then always read from that stored value during guesses. I removed the pattern of regenerating a secret inside normal rerun flow. I also made sure new secret creation only happens in the explicit new-game path. After that change, both manual checks and tests confirmed the secret stayed stable until reset.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.

One habit I want to reuse is pairing quick manual UI checks with targeted pytest runs after each fix. The UI checks helped me catch flow issues, while tests gave me confidence that logic stayed correct. I also want to keep maintaining lightweight project guidance like `CLAUDE.md` so commands, bug context, and expected behavior stay documented while iterating with AI. Finally, I want to continue using `debug.py`-style focused tests to lock in regressions as I fix them.

- What is one thing you would do differently next time you work with AI on a coding task?

Next time, I would define clearer constraints in my prompt before accepting code suggestions, especially expected function behavior and return types. A few confusing suggestions came from not being specific enough about the test contract and current bug symptoms. I would also ask AI to explain why a change is safe before applying it, then verify immediately with a focused test in `debug.py` or pytest. That would reduce time spent validating misleading fixes.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

This project made me treat AI-generated code as a draft that still needs deliberate testing and review. I now see AI as a strong debugging partner when combined with clear docs like `CLAUDE.md` and repeatable checks like `debug.py`, but not a replacement for understanding the runtime behavior and state flow myself.

Additionally, I would have liked to review and practice AI integration with my work, but I have been busy recently with college and extracurricular activities, so I hope to bring this in the next assignment.
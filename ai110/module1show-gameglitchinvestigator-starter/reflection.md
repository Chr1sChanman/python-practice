# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?

It looks like a simple game, with UI that includes buttons for submitting guesss and a new game, a text box area for entering guesses, a hint checkbox, and a section for displaying the score and history of guesses for debugging purposes.

- List at least two concrete bugs you noticed at the start  
(for example: "the secret number kept changing" or "the hints were backwards").

- Game would break after start a new game
- Secret number can exceed number range specified (One instance secret was -35)
- Game gives an incorrect hint (guessing 5; Hint: Go higher)
- Every even number guesss would be converted to str and always fail


---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?

I utilized both Cursor and Claude Code for this project in terms of onboarding and debugging. Cursor was utilized for onboarding and file specific tasks while Claude Code was repo wide summarization and debugging. I utilized both the debug specialization on Cursor and Claude Code for planning major refractoring.


- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

One example of an AI suggestion that was correct was the suggestion to use session state to persist the secret number across rerenders. This was verified by the fact that the secret number no longer changed every time a new game was started.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

One example of the AI suggestion being incorrect was the suggestion to use the `% 2 == 0` to check if the guess was even. This was verified by the fact that the guess was not always converted to a string when it was even.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?

I decided whether a bug was really fixed by running the game and verifying that the bug was no longer present.

- Describe at least one test you ran (manual or using pytest)  
and what it showed you about your code.

I ran the test `test_guess_too_high` to verify that the hint was correct when the guess was too high. This showed me that the hint was correct when the guess was too high.

- Did AI help you design or understand any tests? How?
 
I did utilize AI to draft pytests to test edge cases and behavior of the code. Additionally while it would draft I would also test the system through the UI as well to see any issues that could possible not be caught by the tests.
---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.


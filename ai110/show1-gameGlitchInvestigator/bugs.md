 Unintended Bugs Found in app.py
 (Beyond the 4 documented intentional bugs in CLAUDE.md)

-------------------------------------------------------------------
Bug 1: `status` not reset on New Game (app.py:134-138)
-------------------------------------------------------------------
After winning or losing, clicking "New Game" never resets
st.session_state.status. On rerun, line 140 checks status != "playing"
and calls st.stop() immediately — the game is completely unplayable
after the first win or loss.
Broken code:
  if new_game:
      st.session_state.attempts = 0
      st.session_state.secret = random.randint(1, 100)
      # status is never reset here


 -------------------------------------------------------------------
 Bug 2: `score` and `history` not reset on New Game (app.py:134-138)
 -------------------------------------------------------------------
 Same new_game block never resets score or history. Score accumulates
 across games and history from the previous game pollutes the debug panel.
 A player can never truly start fresh.
 -------------------------------------------------------------------
 Bug 3: New Game ignores difficulty (app.py:136)
 -------------------------------------------------------------------
 Broken code:
   st.session_state.secret = random.randint(1, 100)  # hardcoded

 Uses (1, 100) regardless of the selected difficulty. On Easy (1-20),
 the new secret could be 73 — unguessable within the range shown to
 the player.


 -------------------------------------------------------------------
 Bug 4: st.info hardcodes "1 to 100" regardless of difficulty (app.py:110)
 -------------------------------------------------------------------
 Broken code:
   st.info(f"Guess a number between 1 and 100. Attempts left: ...")

 Should use {low} to {high} (already computed above the call).
 On Easy, the UI tells the player the range is 1-100 when it's 1-20.
 -------------------------------------------------------------------
 Bug 5: Invalid input wastes an attempt (app.py:148, 153)
 -------------------------------------------------------------------
 Broken code:
   if submit:
       st.session_state.attempts += 1   # incremented BEFORE validation
       ok, guess_int, err = parse_guess(raw_guess)
       if not ok:
           st.session_state.history.append(raw_guess)  # garbage in history
           st.error(err)

 Typing "abc" and submitting consumes one of the player's limited attempts
 and appends the raw invalid string to history. Validation errors should
 not penalize the player.
 -------------------------------------------------------------------
 Bug 6: Win score has an off-by-one (app.py:52)
 -------------------------------------------------------------------
 Broken code:
   points = 100 - 10 * (attempt_number + 1)

 The `+ 1` is spurious. On a first-attempt win (attempt_number=2 after
 the increment), this gives 100 - 30 = 70 instead of 100 - 20 = 80.
 Every win yields 10 fewer points than intended.

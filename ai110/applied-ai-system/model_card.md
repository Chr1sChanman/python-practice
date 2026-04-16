# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

Give your model a short, descriptive name.

**Music Matcher 1.0**

---

## 2. Intended Use

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration

This recommender is designed to take audio-related song features (genre, mood, energy, tempo, valence, danceability, acousticness) and score which songs best match a user's vibe profile. The intended audience is mainly students and people interested in music + data experimentation. This is for classroom exploration, not production use, and currently assumes basic CLI use.

---

## 3. How the Model Works

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic

The way this model works is a user profile is defined in `main.py` with weighted genre and mood preferences (0-1), plus target audio values like energy, tempo, valence, danceability, and acousticness. Songs are loaded from `songs.csv`, then each song is scored by combining: (1) weighted genre/mood matches, (2) similarity to target audio values, (3) liked/disliked history bonuses/penalties, and (4) optional artist affinity. After scoring, songs are sorted from highest to lowest score and top-k are returned with an explanation string showing the strongest scoring reasons.

---

## 4. Data

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset

Currently there are 20 songs in the `.csv` file, with diverse genres/moods including pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, reggaeton, metal, classical, drum and bass, country, afrobeat, blues, house, and folk. The numeric values generally align with genre expectations (for example, drum and bass/metal higher BPM and energy, ambient/folk lower BPM and energy, acoustic-focused songs with high acousticness). Even with this expansion, the dataset is still small and does not capture full real-world taste diversity.

---

## 5. Strengths

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition

I think this recommender works well for clearly defined vibe profiles (for example high-energy pop, chill lofi, and acoustic relaxed), and the explanation output helps show exactly why songs ranked where they did. Adding extra profile categories beyond the starter version improved control over recommendations and gave better filtering than just genre + mood alone. The current tests also validate normal behavior and key edge scenarios.

---

## 6. Limitations and Bias

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users

The biggest limitation or bias is that this is still a simple weighted algorithm with a small synthetic catalog. It does not understand lyrics, cultural context, or nuanced emotion beyond the provided fields. Another key limitation is that extreme user weights can overpower audio-feature mismatch (weight inflation case), which is useful to test but also shows the model can be gamed. Conflicting signals like liking and disliking the same song are handled deterministically (+3 and -4), but that may not reflect true user intent. So even when the code behaves as expected, the behavior can still be a design weakness.

---

## 7. Evaluation

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran

The behavior of the recommender is mostly as expected when comparing user profiles against recommended songs and their feature values. I validated this through both CLI runs in `main.py` and pytest coverage (`7 passed`) including normal and adversarial cases. The edge tests include: (1) weight inflation overriding audio mismatch and (2) conflicting likes/dislikes on the same song. These tests passing means the implementation is consistent with the scoring rules, but they also highlight limitations in robustness/fairness that could be improved in future versions.

---

## 8. Future Work

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes

Future work would include adding input validation/clamping for profile weights, better conflict handling for contradictory feedback, and diversity-aware ranking so top results are not too similar. I would also like to add richer metadata (lyrics/themes/language), optional LLM-generated explanations, and a UI frontend for non-CLI users.

---

## 9. Personal Reflection

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps

I learned about the different types of recommendation systems, and further refined on my skills of using AI to help me code. This project makes me wonder what apps like Spotify learn towards in terms of recommender type and how AI has affected how those algorithms work.
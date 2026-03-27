"""
Shared data for the Mood Machine lab.

This file defines:
  - POSITIVE_WORDS: starter list of positive words
  - NEGATIVE_WORDS: starter list of negative words
  - SAMPLE_POSTS: short example posts for evaluation and training
  - TRUE_LABELS: human labels for each post in SAMPLE_POSTS
"""

# ---------------------------------------------------------------------
# Starter word lists
# ---------------------------------------------------------------------

POSITIVE_WORDS = [
    "happy",
    "great",
    "good",
    "love",
    "excited",
    "awesome",
    "fun",
    "chill",
    "relaxed",
    "amazing",
    "hopeful",
    "wonderful",
    "proud",
    "fire",
    "funny",
]

NEGATIVE_WORDS = [
    "sad",
    "bad",
    "terrible",
    "awful",
    "angry",
    "upset",
    "tired",
    "stressed",
    "hate",
    "boring",
    "jealous",
]

# ---------------------------------------------------------------------
# Starter labeled dataset
# ---------------------------------------------------------------------

# Short example posts written as if they were social media updates or messages.
SAMPLE_POSTS = [
    "I love this class so much",
    "Today was a terrible day",
    "Feeling tired but kind of hopeful",
    "This is fine",
    "So excited for the weekend",
    "I am not happy about this"
]

# Human labels for each post above.
# Allowed labels in the starter:
#   - "positive"
#   - "negative"
#   - "neutral"
#   - "mixed"
TRUE_LABELS = [
    "positive",  # "I love this class so much"
    "negative",  # "Today was a terrible day"
    "mixed",     # "Feeling tired but kind of hopeful"
    "neutral",   # "This is fine"
    "positive",  # "So excited for the weekend"
    "negative",  # "I am not happy about this"
]

# TODO: Add 5-10 more posts and labels.
SAMPLE_POSTS += [
    "Oh wonderful, the wifi is down again",           # sarcasm — "wonderful" is misleading
    "Not feeling so great today honestly",            # negation — positive word negated
    "I absolutely love sitting in traffic for hours", # sarcasm — extreme overstatement
    "This playlist is highkey fire no cap",           # slang positive
    "Best day ever!! 😄🎉🙌",                          # emoji-heavy positive
    "I'm literally crying this is so funny 😂💀",     # emoji ambiguity — "crying" looks negative
    "The meeting has been rescheduled to Thursday",   # factual/neutral, no sentiment words
    "It is what it is",                               # resigned neutrality
    "Lowkey stressed but kind of proud of myself",    # mixed — competing emotions
    "Happy for them but also kinda jealous ngl",      # mixed — slang, competing emotions
]

TRUE_LABELS += [
    "negative",  # "Oh wonderful, the wifi is down again"
    "negative",  # "Not feeling so great today honestly"
    "negative",  # "I absolutely love sitting in traffic for hours"
    "positive",  # "This playlist is highkey fire no cap"
    "positive",  # "Best day ever!! 😄🎉🙌"
    "positive",  # "I'm literally crying this is so funny 😂💀"
    "neutral",   # "The meeting has been rescheduled to Thursday"
    "neutral",   # "It is what it is"
    "mixed",     # "Lowkey stressed but kind of proud of myself"
    "mixed",     # "Happy for them but also kinda jealous ngl"
]
'''
SAMPLE_POSTS += [
    "Not bad at all, I'm actually impressed",             # negation of negative word → positive
    "Oh great, another Monday morning meeting 🙄",        # sarcasm + eye-roll emoji → negative
    "I don't hate it",                                    # double negation edge case → positive
    "The package has been delivered",                     # factual, zero sentiment words → neutral
    "Slept 4 hours and have a presentation in 10 mins no big deal 🙃", # sarcasm + upside-down emoji → negative
    "That's actually not terrible ngl",                   # negated negative + slang → positive
    "Feeling 😐 today",                                   # emoji-only sentiment, no words → neutral
    "We love a plot twist 😭",                            # gen-z usage where 😭 = overwhelmed joy → positive
    "Could be worse I guess",                             # resigned acceptance, slight downward lean → mixed
    "Finally finished but I'm completely drained 😮‍💨",   # accomplishment + exhaustion competing → mixed
]

TRUE_LABELS += [
    "positive",  # "Not bad at all, I'm actually impressed"
    "negative",  # "Oh great, another Monday morning meeting 🙄"
    "positive",  # "I don't hate it"
    "neutral",   # "The package has been delivered"
    "negative",  # "Slept 4 hours and have a presentation in 10 mins no big deal 🙃"
    "positive",  # "That's actually not terrible ngl"
    "neutral",   # "Feeling 😐 today"
    "positive",  # "We love a plot twist 😭"
    "mixed",     # "Could be worse I guess"
    "mixed",     # "Finally finished but I'm completely drained 😮‍💨"
]
'''
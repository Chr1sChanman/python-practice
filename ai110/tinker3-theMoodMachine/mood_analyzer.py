# mood_analyzer.py
"""
Rule based mood analyzer for short text snippets.

This class starts with very simple logic:
  - Preprocess the text
  - Look for positive and negative words
  - Compute a numeric score
  - Convert that score into a mood label
"""

import re
from typing import List, Dict, Tuple, Optional

from dataset import POSITIVE_WORDS, NEGATIVE_WORDS


class MoodAnalyzer:
    """
    A very simple, rule based mood classifier.
    """

    def __init__(
        self,
        positive_words: Optional[List[str]] = None,
        negative_words: Optional[List[str]] = None,
    ) -> None:
        # Use the default lists from dataset.py if none are provided.
        positive_words = positive_words if positive_words is not None else POSITIVE_WORDS
        negative_words = negative_words if negative_words is not None else NEGATIVE_WORDS

        # Store as sets for faster lookup.
        self.positive_words = set(w.lower() for w in positive_words)
        self.negative_words = set(w.lower() for w in negative_words)

    # ---------------------------------------------------------------------
    # Preprocessing
    # ---------------------------------------------------------------------

    def preprocess(self, text: str) -> List[str]:
        """
        Convert raw text into a list of tokens the model can work with.

        TODO: Improve this method.

        Right now, it does the minimum:
          - Strips leading and trailing whitespace
          - Converts everything to lowercase
          - Splits on spaces

        Ideas to improve:
          - Remove punctuation
          - Handle simple emojis separately (":)", ":-(", "🥲", "😂")
          - Normalize repeated characters ("soooo" -> "soo")
        """
        cleaned = text.strip().lower()
        tokens = []

        # Extract emoji signals before stripping punctuation.
        pos_emojis = {"😄", "🎉", "😂", "🙌", "❤️"}
        neg_emojis = {"😢", "🙄", "🙃", "😡"}
        for ch in cleaned:
            if ch in pos_emojis:
                tokens.append("__emoji_pos__")
            elif ch in neg_emojis:
                tokens.append("__emoji_neg__")

        # Remove punctuation, normalize repeated chars (e.g. "soooo" -> "soo"), then split.
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        for word in cleaned.split():
            word = re.sub(r'(.)\1{2,}', r'\1\1', word)
            tokens.append(word)

        return tokens

    # ---------------------------------------------------------------------
    # Scoring logic
    # ---------------------------------------------------------------------

    def score_text(self, text: str) -> int:
        """
        Compute a numeric "mood score" for the given text.

        Positive words increase the score.
        Negative words decrease the score.

        TODO: You must choose AT LEAST ONE modeling improvement to implement.
        For example:
          - Handle simple negation such as "not happy" or "not bad"
          - Count how many times each word appears instead of just presence
          - Give some words higher weights than others (for example "hate" < "annoyed")
          - Treat emojis or slang (":)", "lol", "💀") as strong signals
        """
        tokens = self.preprocess(text)
        score = 0
        negate = False
        negation_words = {"not", "no", "never", "dont", "didnt", "isnt", "wasnt", "cant", "wont"}

        for token in tokens:
            if token in negation_words:
                negate = True
                continue

            points = 0
            if token in self.positive_words or token == "__emoji_pos__":
                points = 1
            elif token in self.negative_words or token == "__emoji_neg__":
                points = -1

            if points != 0:
                score += -points if negate else points
                negate = False

        return score

    # ---------------------------------------------------------------------
    # Label prediction
    # ---------------------------------------------------------------------

    def predict_label(self, text: str) -> str:
        """
        Turn the numeric score for a piece of text into a mood label.

        The default mapping is:
          - score > 0  -> "positive"
          - score < 0  -> "negative"
          - score == 0 -> "neutral"

        TODO: You can adjust this mapping if it makes sense for your model.
        For example:
          - Use different thresholds (for example score >= 2 to be "positive")
          - Add a "mixed" label for scores close to zero
        Just remember that whatever labels you return should match the labels
        you use in TRUE_LABELS in dataset.py if you care about accuracy.
        """
        score = self.score_text(text)
        if score >= 1:
            return "positive"
        elif score <= -1:
            return "negative"
        else:
            # score is 0 — check if both positive and negative words are present (mixed vs neutral).
            tokens = self.preprocess(text)
            has_pos = any(t in self.positive_words for t in tokens)
            has_neg = any(t in self.negative_words for t in tokens)
            # region agent log
            import json as _json
            with open("/Users/christopherchan/Documents/python-practice/ai110/ai110-module3tinker-themoodmachine-starter/.cursor/debug-2f96a1.log", "a") as _f:
                _f.write(_json.dumps({"sessionId":"2f96a1","location":"mood_analyzer.py:predict_label","message":"zero-score branch","data":{"text":text,"score":score,"has_pos":has_pos,"has_neg":has_neg,"tokens":tokens},"timestamp":__import__('time').time()}) + "\n")
            # endregion agent log
            if has_pos and has_neg:
                return "mixed"
            return "neutral"

    # ---------------------------------------------------------------------
    # Explanations (optional but recommended)
    # ---------------------------------------------------------------------

    def explain(self, text: str) -> str:
        """
        Return a short string explaining WHY the model chose its label.

        TODO:
          - Look at the tokens and identify which ones counted as positive
            and which ones counted as negative.
          - Show the final score.
          - Return a short human readable explanation.

        Example explanation (your exact wording can be different):
          'Score = 2 (positive words: ["love", "great"]; negative words: [])'

        The current implementation is a placeholder so the code runs even
        before you implement it.
        """
        tokens = self.preprocess(text)

        positive_hits: List[str] = []
        negative_hits: List[str] = []
        score = 0

        for token in tokens:
            if token in self.positive_words:
                positive_hits.append(token)
                score += 1
            if token in self.negative_words:
                negative_hits.append(token)
                score -= 1

        return (
            f"Score = {score} "
            f"(positive: {positive_hits or '[]'}, "
            f"negative: {negative_hits or '[]'})"
        )

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run rule-based classifier (evaluation + batch demo + interactive loop)
python main.py

# Run ML classifier (train + evaluate + interactive loop)
python ml_experiments.py
```

There is no test framework — correctness is verified by running the scripts and observing printed output.

## Architecture

This is an educational text classification lab with two parallel approaches:

**Rule-based pipeline** (`dataset.py` → `mood_analyzer.py` → `main.py`)
- `dataset.py` defines word lists (`POSITIVE_WORDS`, `NEGATIVE_WORDS`) and labeled examples (`SAMPLE_POSTS`, `TRUE_LABELS`)
- `mood_analyzer.py` implements `MoodAnalyzer`: `preprocess()` → `score_text()` → `predict_label()` → `explain()`
- `main.py` orchestrates evaluation against true labels, a batch demo, and an interactive CLI

**ML pipeline** (all in `ml_experiments.py`)
- Uses the same `SAMPLE_POSTS`/`TRUE_LABELS` from `dataset.py`
- Trains a `LogisticRegression` with `CountVectorizer` (bag-of-words) on the labeled dataset
- Evaluates accuracy, supports single-text prediction, and runs an interactive CLI

Both pipelines produce the same label set: `"positive"`, `"negative"`, `"neutral"`, `"mixed"`.

## Key TODOs (student work)

- `mood_analyzer.py`: `score_text()` and `predict_label()` contain the core classification logic students implement
- `dataset.py`: `SAMPLE_POSTS`/`TRUE_LABELS` should be expanded with diverse examples (slang, emojis, sarcasm, mixed emotions)
- `model_card.md`: Template for reflecting on model behavior, limitations, and fairness after experiments

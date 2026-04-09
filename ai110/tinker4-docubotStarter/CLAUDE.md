# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This is a teaching project (AI 110 tinker activity) structured as a progressive three-phase build:

- **Phase 0 — Naive LLM** (`llm_client.py`): `GeminiClient.naive_answer_over_full_docs` sends the full corpus to Gemini. Currently the prompt ignores `all_text` — that's intentional starter code for students to fix.
- **Phase 1 — Retrieval** (`docubot.py`): Implemented. `build_index` builds a normalized inverted index, `score_document` uses stopword-filtered word-overlap scoring, and `retrieve` does paragraph-level chunking with a score guardrail.
- **Phase 2 — RAG** (`llm_client.py`): `GeminiClient.answer_from_snippets` takes the retrieved snippets and prompts Gemini to answer using only them.

**Data flow:**
```
main.py → DocuBot (docubot.py) → retrieve snippets from docs/
                               ↘ GeminiClient (llm_client.py) → Gemini API
```

**Key files to modify:**
- `docubot.py` — retrieval index, scoring, snippet selection
- `llm_client.py` — prompts for naive and RAG modes
- `dataset.py` — `SAMPLE_QUERIES` for testing; `FALLBACK_DOCS` if `docs/` is missing

**Evaluation** (`evaluation.py`): `EXPECTED_SOURCES` maps query substrings to expected filenames. `evaluate_retrieval` checks retrieval hit rate against `SAMPLE_QUERIES`.

## Model

The Gemini model is set via `GEMINI_MODEL_NAME = "gemini-2.5-flash"` in `llm_client.py`.

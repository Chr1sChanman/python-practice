# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

This project is in the design phase. No implementation exists yet — the repo currently contains only a feature spec and a UML draft.

## Planned Architecture

Based on `bytebites_spec.md`, the backend will model four classes:

- **Customer** — has a `name`, a `purchase_history` (list of Transactions), and a `verify_user()` method
- **Item** — has `name`, `price`, `popularity_rating`; belongs to a `Category`
- **Transaction** — aggregates one or more `Item` objects; computes `total_cost`
- **Category** — groups `Item` objects and supports filtering

See `uml_draft.md` for the Mermaid class diagram with relationships.

## Key Relationships

- `Customer` → `Transaction` (one-to-many, via purchase history)
- `Transaction` aggregates `Item` (one-to-many)
- `Category` aggregates `Item` (one-to-many)

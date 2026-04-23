"""
Evaluation harness for the music recommender.

Computes ranking-quality metrics (nDCG, precision, recall) per profile and
system-level metrics (coverage, genre entropy) across all profiles, against
hand-labeled ground truth in data/eval_profiles.json.

Usage:
    python -m src.eval                      # default config
    python -m src.eval --k 5                # top-k cutoff
    python -m src.eval --eval-path ...      # custom labels
"""
from __future__ import annotations

import argparse
import json
import math
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.config import ScoringConfig
from src.recommender import UserProfile, load_songs, recommend_songs


# Pure metric functions
def dcg_at_k(relevances: List[int], k: int) -> float:
    """
    Discounted Cumulative Gain over a relevance list (already in rank order).

    DCG = sum_{i=1..k} rel_i / log2(i + 1)
    """
    if k <= 0:
        return 0.0
    return sum(
        rel / math.log2(i + 2)  # i is 0-indexed, so position 1 -> log2(2) = 1
        for i, rel in enumerate(relevances[:k])
    )


def ndcg_at_k(
    predicted_ids: List[int],
    relevance: Dict[int, int],
    k: int,
) -> float:
    """
    Normalized DCG@k. Returns a value in [0, 1] (1.0 = ideal ranking).

    Compares the DCG of the predicted ordering against the IDEAL DCG (the
    DCG you would have gotten by picking the highest-relevance items first).
    """
    pred_rels = [relevance.get(sid, 0) for sid in predicted_ids[:k]]
    ideal_rels = sorted(relevance.values(), reverse=True)[:k]
    dcg = dcg_at_k(pred_rels, k)
    idcg = dcg_at_k(ideal_rels, k)
    return dcg / idcg if idcg > 0 else 0.0


def precision_at_k(
    predicted_ids: List[int],
    relevance: Dict[int, int],
    k: int,
    threshold: int = 1,
) -> float:
    """Fraction of top-k predictions whose relevance >= threshold."""
    if k <= 0:
        return 0.0
    hits = sum(1 for sid in predicted_ids[:k] if relevance.get(sid, 0) >= threshold)
    return hits / k


def recall_at_k(
    predicted_ids: List[int],
    relevance: Dict[int, int],
    k: int,
    threshold: int = 1,
) -> float:
    """Fraction of all relevant items (>= threshold) that appear in top-k."""
    relevant_total = sum(1 for v in relevance.values() if v >= threshold)
    if relevant_total == 0:
        return 0.0
    hits = sum(1 for sid in predicted_ids[:k] if relevance.get(sid, 0) >= threshold)
    return hits / relevant_total


def coverage(
    predicted_ids_across_profiles: List[List[int]],
    catalog_size: int,
) -> float:
    """
    Fraction of catalog that ever appears in any profile's top-k.

    Low coverage = the recommender keeps recycling the same songs.
    """
    if catalog_size <= 0:
        return 0.0
    seen = set()
    for ids in predicted_ids_across_profiles:
        seen.update(ids)
    return len(seen) / catalog_size


def genre_entropy(predicted_songs: List[dict]) -> float:
    """
    Shannon entropy (bits) of the genre distribution in one result list.

    0.0 = all the same genre. log2(N) = perfectly diverse across N genres.
    """
    if not predicted_songs:
        return 0.0
    counts: Dict[str, int] = {}
    for s in predicted_songs:
        g = s.get("genre", "unknown")
        counts[g] = counts.get(g, 0) + 1
    total = sum(counts.values())
    return -sum(
        (c / total) * math.log2(c / total)
        for c in counts.values()
        if c > 0
    )


# Evaluation runner
@dataclass
class EvalReport:
    """Result of evaluating a config against a labeled profile set."""
    per_profile: Dict[str, Dict[str, float]] = field(default_factory=dict)
    aggregate: Dict[str, float] = field(default_factory=dict)
    invariant_violations: List[str] = field(default_factory=list)
    guardrail_violations: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not (self.invariant_violations or self.guardrail_violations)


def _load_eval_profiles(eval_path: str) -> List[Tuple[str, UserProfile, Dict[int, int]]]:
    """Read eval_profiles.json -> list of (name, UserProfile, relevance dict)."""
    raw = json.loads(Path(eval_path).read_text())
    out: List[Tuple[str, UserProfile, Dict[int, int]]] = []
    for entry in raw["profiles"]:
        name = entry["name"]
        profile = UserProfile(**entry["profile"])
        relevance = {int(sid): int(grade) for sid, grade in entry["relevance"].items()}
        out.append((name, profile, relevance))
    return out


def evaluate(
    config: Optional[ScoringConfig] = None,
    eval_path: str = "data/eval_profiles.json",
    songs_path: str = "data/songs.csv",
    k: int = 5,
) -> EvalReport:
    """
    Run the recommender against every labeled profile and compute metrics.

    Returns an EvalReport with per-profile scores plus aggregate means and
    coverage. Any UserWarning emitted during a run is recorded in
    ``guardrail_violations`` so a tuner can spot regressions.
    """
    if config is None:
        config = ScoringConfig()

    songs = load_songs(songs_path)
    catalog_size = len(songs)
    eval_set = _load_eval_profiles(eval_path)

    report = EvalReport()
    all_top_ids: List[List[int]] = []

    for name, profile, relevance in eval_set:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            ranked = recommend_songs(profile, songs, k=k, config=config)

        for w in caught:
            if issubclass(w.category, UserWarning):
                report.guardrail_violations.append(f"{name}: {w.message}")

        predicted_ids = [s["id"] for s, _, _ in ranked]
        predicted_songs = [s for s, _, _ in ranked]
        all_top_ids.append(predicted_ids)

        report.per_profile[name] = {
            "ndcg@k": round(ndcg_at_k(predicted_ids, relevance, k), 4),
            "precision@k": round(precision_at_k(predicted_ids, relevance, k), 4),
            "recall@k": round(recall_at_k(predicted_ids, relevance, k), 4),
            "genre_entropy": round(genre_entropy(predicted_songs), 4),
        }

    n = max(len(report.per_profile), 1)
    report.aggregate = {
        "mean_ndcg": round(sum(p["ndcg@k"] for p in report.per_profile.values()) / n, 4),
        "mean_precision": round(sum(p["precision@k"] for p in report.per_profile.values()) / n, 4),
        "mean_recall": round(sum(p["recall@k"] for p in report.per_profile.values()) / n, 4),
        "mean_genre_entropy": round(sum(p["genre_entropy"] for p in report.per_profile.values()) / n, 4),
        "coverage": round(coverage(all_top_ids, catalog_size), 4),
        "k": k,
        "catalog_size": catalog_size,
        "n_profiles": n,
    }
    return report


# Markdown rendering + CLI
def report_to_markdown(report: EvalReport, config: ScoringConfig) -> str:
    """Render an EvalReport as a human-readable markdown string."""
    lines: List[str] = []
    lines.append("# Recommender Evaluation Report")
    lines.append("")
    lines.append(f"- k = {report.aggregate.get('k')}")
    lines.append(f"- catalog size = {report.aggregate.get('catalog_size')}")
    lines.append(f"- profiles evaluated = {report.aggregate.get('n_profiles')}")
    lines.append(f"- passed (no invariant/guardrail violations) = **{report.passed}**")
    lines.append("")
    lines.append("## Per-profile metrics")
    lines.append("")
    lines.append("| Profile | nDCG@k | Precision@k | Recall@k | Genre Entropy |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for name, m in report.per_profile.items():
        lines.append(
            f"| {name} | {m['ndcg@k']:.4f} | {m['precision@k']:.4f} | "
            f"{m['recall@k']:.4f} | {m['genre_entropy']:.4f} |"
        )
    lines.append("")
    lines.append("## Aggregate metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | ---: |")
    for key in ("mean_ndcg", "mean_precision", "mean_recall", "mean_genre_entropy", "coverage"):
        lines.append(f"| {key} | {report.aggregate[key]:.4f} |")
    lines.append("")
    lines.append("## Scoring config used")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(config.to_dict(), indent=2))
    lines.append("```")
    if report.guardrail_violations:
        lines.append("")
        lines.append("## Guardrail violations")
        for v in report.guardrail_violations:
            lines.append(f"- {v}")
    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the music recommender.")
    parser.add_argument("--k", type=int, default=5, help="top-k cutoff (default 5)")
    parser.add_argument("--eval-path", default="data/eval_profiles.json")
    parser.add_argument("--songs-path", default="data/songs.csv")
    parser.add_argument("--out", default="evidence/eval_latest.md")
    args = parser.parse_args(argv)

    config = ScoringConfig()
    report = evaluate(
        config=config,
        eval_path=args.eval_path,
        songs_path=args.songs_path,
        k=args.k,
    )

    md = report_to_markdown(report, config)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)

    print(md)
    print(f"\n(report written to {out_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

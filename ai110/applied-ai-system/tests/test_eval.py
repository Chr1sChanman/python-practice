"""
Phase 3 tests: evaluation metric correctness and runner integration.
"""
import math

import pytest

from src.config import ScoringConfig
from src.eval import (
    coverage,
    dcg_at_k,
    evaluate,
    genre_entropy,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


# nDCG core behavior
def test_ndcg_perfect_ranking_is_one():
    """If we predict the ideal ordering, nDCG must be exactly 1.0."""
    relevance = {1: 2, 2: 2, 3: 1, 4: 0}
    predicted = [1, 2, 3, 4]
    assert ndcg_at_k(predicted, relevance, k=4) == pytest.approx(1.0)


def test_ndcg_reversed_worse_than_ordered():
    relevance = {1: 2, 2: 1, 3: 0}
    ordered = ndcg_at_k([1, 2, 3], relevance, k=3)
    reversed_ = ndcg_at_k([3, 2, 1], relevance, k=3)
    assert ordered > reversed_


def test_ndcg_only_irrelevant_items_is_zero():
    relevance = {1: 2, 2: 1}
    assert ndcg_at_k([99, 100], relevance, k=2) == 0.0


def test_ndcg_no_labels_returns_zero():
    """If no items have non-zero relevance, IDCG = 0 -> nDCG = 0."""
    assert ndcg_at_k([1, 2, 3], {1: 0, 2: 0}, k=3) == 0.0


# DCG
def test_dcg_position_discount():
    """A relevance-2 hit at position 1 is worth more than at position 2."""
    pos1 = dcg_at_k([2, 0], k=2)
    pos2 = dcg_at_k([0, 2], k=2)
    assert pos1 > pos2
    assert pos1 == pytest.approx(2.0 / math.log2(2))    # log2(2) = 1
    assert pos2 == pytest.approx(2.0 / math.log2(3))


# Precision / Recall
def test_precision_respects_threshold():
    relevance = {1: 2, 2: 1, 3: 0}
    # threshold=1: ids 1 and 2 count -> 2/3
    assert precision_at_k([1, 2, 3], relevance, k=3, threshold=1) == pytest.approx(2 / 3)
    # threshold=2: only id 1 counts -> 1/3
    assert precision_at_k([1, 2, 3], relevance, k=3, threshold=2) == pytest.approx(1 / 3)


def test_recall_finds_all_relevant():
    relevance = {1: 2, 2: 1, 3: 0, 4: 2}
    # 3 relevant ids (1, 2, 4); top-2 captures 2 of them
    assert recall_at_k([1, 2], relevance, k=2, threshold=1) == pytest.approx(2 / 3)


# Coverage / Entropy
def test_coverage_unique_across_profiles():
    # 2 profiles, top-3 each, with overlap; 4 unique songs out of 10 catalog
    assert coverage([[1, 2, 3], [3, 4, 1]], catalog_size=10) == pytest.approx(0.4)


def test_genre_entropy_uniform_vs_monoculture():
    songs_uniform = [{"genre": "a"}, {"genre": "b"}, {"genre": "c"}, {"genre": "d"}]
    songs_mono = [{"genre": "pop"}] * 4
    assert genre_entropy(songs_uniform) == pytest.approx(2.0)  # log2(4)
    assert genre_entropy(songs_mono) == 0.0


# evaluate() integration
def test_evaluate_default_config_returns_metrics():
    """evaluate() runs end-to-end and produces sensible aggregate numbers."""
    report = evaluate(config=ScoringConfig(), k=5)
    assert "mean_ndcg" in report.aggregate
    assert 0.0 <= report.aggregate["mean_ndcg"] <= 1.0
    assert 0.0 <= report.aggregate["coverage"] <= 1.0
    assert report.aggregate["n_profiles"] == 5
    assert len(report.per_profile) == 5
    # Default config should beat random; expect nontrivial nDCG
    assert report.aggregate["mean_ndcg"] > 0.5


def test_evaluate_zero_weights_underperforms_default():
    """A bad config (all zero weights) should score lower than the defaults."""
    bad = ScoringConfig(
        w_genre=0, w_mood=0, w_energy=0, w_tempo=0,
        w_valence=0, w_dance=0, w_acoustic=0, w_artist=0,
        w_liked=0, w_disliked=0,
    )
    bad_report = evaluate(config=bad, k=5)
    good_report = evaluate(config=ScoringConfig(), k=5)
    assert good_report.aggregate["mean_ndcg"] >= bad_report.aggregate["mean_ndcg"]

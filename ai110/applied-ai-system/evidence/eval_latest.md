# Recommender Evaluation Report

- k = 5
- catalog size = 20
- profiles evaluated = 5
- passed (no invariant/guardrail violations) = **True**

## Per-profile metrics

| Profile | nDCG@k | Precision@k | Recall@k | Genre Entropy |
| --- | ---: | ---: | ---: | ---: |
| High-Energy Pop | 0.9218 | 1.0000 | 0.7143 | 1.9219 |
| Chill Lofi | 1.0000 | 1.0000 | 0.6250 | 1.3710 |
| Deep Intense Rock | 1.0000 | 1.0000 | 1.0000 | 2.3219 |
| Acoustic Relaxed | 1.0000 | 1.0000 | 0.6250 | 2.3219 |
| Night Drive Moody | 0.7929 | 0.6000 | 0.6000 | 2.3219 |

## Aggregate metrics

| Metric | Value |
| --- | ---: |
| mean_ndcg | 0.9429 |
| mean_precision | 0.9200 |
| mean_recall | 0.7129 |
| mean_genre_entropy | 2.0517 |
| coverage | 0.9000 |

## Scoring config used

```json
{
  "w_genre": 1.25,
  "w_mood": 2.0,
  "w_energy": 4.0,
  "w_tempo": 1.2,
  "w_valence": 1.0,
  "w_dance": 1.0,
  "w_acoustic": 1.0,
  "w_artist": 1.0,
  "w_liked": 3.0,
  "w_disliked": -4.0
}
```

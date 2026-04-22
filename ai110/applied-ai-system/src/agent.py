"""
WeightTuningAgent: a bounded plan/act/check/decide loop that searches for
ScoringConfig improvements without breaking invariants.

This is the agentic-workflow feature. It is intentionally small:
- Plan = pick one weight to perturb (seeded RNG).
- Act  = produce a candidate ScoringConfig with the delta applied + clamped.
- Check= call src.eval.evaluate to score the candidate.
- Decide=accept iff after.passed AND mean_ndcg did not regress.

Stops when budget is exhausted OR patience iterations pass without strict
improvement. Every iteration is logged as one JSON line to logs/agent.jsonl.

Usage:
    python -m src.agent --budget 20 --seed 0
"""
from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import List, Optional, Tuple

from src.config import ScoringConfig
from src.eval import EvalReport, evaluate, report_to_markdown
from src.logging_utils import get_logger, log_event


# Bounds for each weight. w_disliked is the only weight that should stay
# negative; everything else stays >= 0.
WEIGHT_BOUNDS = {
    "w_genre": (0.0, 20.0),
    "w_mood": (0.0, 20.0),
    "w_energy": (0.0, 20.0),
    "w_tempo": (0.0, 20.0),
    "w_valence": (0.0, 20.0),
    "w_dance": (0.0, 20.0),
    "w_acoustic": (0.0, 20.0),
    "w_artist": (0.0, 20.0),
    "w_liked": (0.0, 20.0),
    "w_disliked": (-20.0, 0.0),
}
TUNABLE_WEIGHTS: List[str] = list(WEIGHT_BOUNDS.keys())


@dataclass
class Action:
    """A proposed perturbation to one weight."""
    weight_name: str
    delta: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Step:
    """One iteration of the agent loop."""
    iteration: int
    action: Action
    before: ScoringConfig
    after: ScoringConfig
    report_before: EvalReport
    report_after: EvalReport
    accepted: bool
    reason: str


class WeightTuningAgent:
    """
    Hill-climbing agent over ScoringConfig weights.

    Args:
        seed: RNG seed for reproducibility.
        step_size: magnitude of each weight perturbation.
        eval_path / songs_path / k: forwarded to evaluate().
        starting_config: optional config to start from (defaults to ScoringConfig()).
        patience: stop early after this many iterations without strict improvement.
        log_path: where to append per-step JSON lines.
    """

    def __init__(
        self,
        seed: int = 0,
        step_size: float = 0.25,
        eval_path: str = "data/eval_profiles.json",
        songs_path: str = "data/songs.csv",
        k: int = 5,
        starting_config: Optional[ScoringConfig] = None,
        patience: int = 5,
        log_path: str = "logs/agent.jsonl",
    ) -> None:
        self.rng = random.Random(seed)
        self.step_size = step_size
        self.eval_path = eval_path
        self.songs_path = songs_path
        self.k = k
        self.starting_config = starting_config or ScoringConfig()
        self.patience = patience
        self.log_path = log_path
        # Use a logger name that is unique to this log_path so that creating
        # multiple agents (e.g. across tests with different tmp paths) does
        # not reuse a cached handler bound to a stale file.
        self._logger = get_logger(f"agent::{log_path}", log_path=log_path)
        self._seed = seed

    # ---- The four loop primitives ----

    def plan(
        self,
        current: ScoringConfig,
        history: List[Step],
    ) -> Action:
        """Choose a random weight and a +/- step_size delta."""
        weight_name = self.rng.choice(TUNABLE_WEIGHTS)
        sign = self.rng.choice([-1.0, 1.0])
        return Action(weight_name=weight_name, delta=sign * self.step_size)

    def act(self, current: ScoringConfig, action: Action) -> ScoringConfig:
        """Apply the action and clamp to the weight's allowed bounds."""
        lo, hi = WEIGHT_BOUNDS[action.weight_name]
        new_value = getattr(current, action.weight_name) + action.delta
        new_value = max(lo, min(hi, new_value))
        return replace(current, **{action.weight_name: new_value})

    def check(self, candidate: ScoringConfig) -> EvalReport:
        """Score the candidate against the labeled eval set."""
        return evaluate(
            config=candidate,
            eval_path=self.eval_path,
            songs_path=self.songs_path,
            k=self.k,
        )

    def decide(
        self,
        before: EvalReport,
        after: EvalReport,
    ) -> Tuple[bool, str]:
        """Accept iff guardrails pass and mean_ndcg did not regress."""
        if not after.passed:
            return False, (
                f"rejected: guardrail/invariant violations "
                f"({len(after.guardrail_violations)} guard, "
                f"{len(after.invariant_violations)} invariant)"
            )
        before_n = before.aggregate.get("mean_ndcg", 0.0)
        after_n = after.aggregate.get("mean_ndcg", 0.0)
        if after_n >= before_n:
            tag = "improved" if after_n > before_n else "tied"
            return True, f"accepted ({tag}): mean_ndcg {before_n:.4f} -> {after_n:.4f}"
        return False, f"rejected: mean_ndcg regressed {before_n:.4f} -> {after_n:.4f}"

    # ---- The driver ----

    def run(self, budget: int = 20) -> List[Step]:
        """Run up to ``budget`` iterations or stop early via patience."""
        current = self.starting_config
        report_current = self.check(current)
        best_ndcg = report_current.aggregate["mean_ndcg"]
        history: List[Step] = []
        no_improve_streak = 0

        log_event(
            self._logger,
            "agent_start",
            seed=self._seed,
            step_size=self.step_size,
            budget=budget,
            patience=self.patience,
            starting_config=current.to_dict(),
            starting_mean_ndcg=round(best_ndcg, 4),
        )

        for iteration in range(1, budget + 1):
            action = self.plan(current, history)
            candidate = self.act(current, action)
            report_after = self.check(candidate)
            accepted, reason = self.decide(report_current, report_after)

            step = Step(
                iteration=iteration,
                action=action,
                before=current,
                after=candidate,
                report_before=report_current,
                report_after=report_after,
                accepted=accepted,
                reason=reason,
            )
            history.append(step)

            log_event(
                self._logger,
                "agent_step",
                iteration=iteration,
                action=action.to_dict(),
                before_config=current.to_dict(),
                after_config=candidate.to_dict(),
                before_mean_ndcg=round(report_current.aggregate["mean_ndcg"], 4),
                after_mean_ndcg=round(report_after.aggregate["mean_ndcg"], 4),
                accepted=accepted,
                reason=reason,
            )

            if accepted:
                current = candidate
                if report_after.aggregate["mean_ndcg"] > best_ndcg:
                    best_ndcg = report_after.aggregate["mean_ndcg"]
                    no_improve_streak = 0
                else:
                    no_improve_streak += 1
                report_current = report_after
            else:
                no_improve_streak += 1

            if no_improve_streak >= self.patience:
                log_event(
                    self._logger,
                    "agent_stop",
                    reason="patience_exhausted",
                    iterations_run=iteration,
                    best_mean_ndcg=round(best_ndcg, 4),
                )
                break
        else:
            log_event(
                self._logger,
                "agent_stop",
                reason="budget_exhausted",
                iterations_run=budget,
                best_mean_ndcg=round(best_ndcg, 4),
            )

        return history


# --------------------------------------------------------------------------
# Report rendering + CLI
# --------------------------------------------------------------------------

def _ascii_chart(values: List[float], width: int = 40) -> str:
    """Render a tiny ASCII bar chart of float values, normalized to [0, width]."""
    if not values:
        return "(empty)"
    lo, hi = min(values), max(values)
    span = hi - lo if hi > lo else 1.0
    lines = []
    for i, v in enumerate(values, start=1):
        bar_len = int(((v - lo) / span) * width)
        bar = "#" * bar_len
        lines.append(f"  iter {i:>3} | {v:.4f} | {bar}")
    return "\n".join(lines)


def write_report(
    history: List[Step],
    starting: ScoringConfig,
    final: ScoringConfig,
    out_path: str = "evidence/agent_report.md",
) -> str:
    """Write a markdown summary of one agent run; return its path."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if history:
        before_ndcg = history[0].report_before.aggregate["mean_ndcg"]
        after_ndcg = history[-1].report_after.aggregate["mean_ndcg"]
        accepted = [s for s in history if s.accepted]
        trajectory = [s.report_after.aggregate["mean_ndcg"] for s in history]
    else:
        before_ndcg = after_ndcg = 0.0
        accepted = []
        trajectory = []

    lines: List[str] = []
    lines.append("# WeightTuningAgent Run Report")
    lines.append("")
    lines.append(f"- iterations run: **{len(history)}**")
    lines.append(f"- accepted steps: **{len(accepted)}**")
    lines.append(f"- starting mean_ndcg: **{before_ndcg:.4f}**")
    lines.append(f"- ending mean_ndcg: **{after_ndcg:.4f}**")
    lines.append(f"- net change: **{after_ndcg - before_ndcg:+.4f}**")
    lines.append("")
    lines.append("## Final config")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(final.to_dict(), indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## Starting config")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(starting.to_dict(), indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## Accepted actions")
    lines.append("")
    if accepted:
        lines.append("| Iter | Weight | Delta | Before nDCG | After nDCG |")
        lines.append("| ---: | --- | ---: | ---: | ---: |")
        for s in accepted:
            lines.append(
                f"| {s.iteration} | {s.action.weight_name} | "
                f"{s.action.delta:+.2f} | "
                f"{s.report_before.aggregate['mean_ndcg']:.4f} | "
                f"{s.report_after.aggregate['mean_ndcg']:.4f} |"
            )
    else:
        lines.append("(none accepted)")
    lines.append("")
    lines.append("## Mean nDCG trajectory (per iteration, after step)")
    lines.append("")
    lines.append("```")
    lines.append(_ascii_chart(trajectory))
    lines.append("```")

    out.write_text("\n".join(lines) + "\n")
    return str(out)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the WeightTuningAgent.")
    parser.add_argument("--budget", type=int, default=20, help="max iterations (default 20)")
    parser.add_argument("--seed", type=int, default=0, help="RNG seed (default 0)")
    parser.add_argument("--step-size", type=float, default=0.25)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--eval-path", default="data/eval_profiles.json")
    parser.add_argument("--songs-path", default="data/songs.csv")
    parser.add_argument("--log-path", default="logs/agent.jsonl")
    parser.add_argument("--out", default="evidence/agent_report.md")
    parser.add_argument(
        "--save-config",
        default=None,
        help="optional path to save the tuned ScoringConfig as JSON",
    )
    args = parser.parse_args(argv)

    starting = ScoringConfig()
    agent = WeightTuningAgent(
        seed=args.seed,
        step_size=args.step_size,
        eval_path=args.eval_path,
        songs_path=args.songs_path,
        k=args.k,
        starting_config=starting,
        patience=args.patience,
        log_path=args.log_path,
    )
    history = agent.run(budget=args.budget)

    final = history[-1].after if history and history[-1].accepted else (
        history[-1].before if history else starting
    )
    # Walk forward to find the actual current config (last accepted state).
    current = starting
    for s in history:
        if s.accepted:
            current = s.after
    final = current

    report_path = write_report(history, starting, final, out_path=args.out)
    final_eval = evaluate(
        config=final, eval_path=args.eval_path, songs_path=args.songs_path, k=args.k
    )
    print(report_to_markdown(final_eval, final))
    print(f"\n(agent report: {report_path})")
    print(f"(agent log: {args.log_path})")

    if args.save_config:
        Path(args.save_config).parent.mkdir(parents=True, exist_ok=True)
        Path(args.save_config).write_text(json.dumps(final.to_dict(), indent=2) + "\n")
        print(f"(tuned config saved to: {args.save_config})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

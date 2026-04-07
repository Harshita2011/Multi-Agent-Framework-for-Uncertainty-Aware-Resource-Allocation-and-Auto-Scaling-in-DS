"""Run the publication-grade evaluation suite with broad baselines and ablations."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
RUN_BATCH_PATH = ROOT_DIR / "experiments" / "run_batch.py"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run publication-grade suite (baseline breadth + ablations + repeated statistics)."
    )
    parser.add_argument("--batch-name", default="publication-suite", help="Batch name under results/<name>/")
    parser.add_argument("--runs-per-scenario", type=int, default=30, help="Repeated runs per scenario (recommended >= 30)")
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Continue remaining scenarios even if one run fails.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    command = [
        sys.executable,
        str(RUN_BATCH_PATH),
        "--batch-name",
        args.batch_name,
        "--runs-per-scenario",
        str(args.runs_per_scenario),
        "--scenario",
        "proposed=experiments/configs/proposed_baseline_long.yaml",
        "--scenario",
        "threshold=experiments/configs/threshold_baseline_long.yaml",
        "--scenario",
        "reactive=experiments/configs/reactive_baseline_long.yaml",
        "--scenario",
        "hpa-like=experiments/configs/hpa_like_baseline_long.yaml",
        "--scenario",
        "predictive-only=experiments/configs/predictive_only_baseline_long.yaml",
        "--scenario",
        "ablation-no-risk=experiments/configs/ablation_no_risk_baseline_long.yaml",
        "--scenario",
        "ablation-no-uncertainty=experiments/configs/ablation_no_uncertainty_baseline_long.yaml",
        "--scenario",
        "ablation-no-agents=experiments/configs/ablation_no_agents_baseline_long.yaml",
        "--scenario",
        "replay-trace=experiments/configs/replay_trace_long.yaml",
    ]
    if args.continue_on_failure:
        command.append("--continue-on-failure")

    completed = subprocess.run(command, cwd=ROOT_DIR, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())

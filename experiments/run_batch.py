"""Run repeated experiment scenarios and aggregate the results."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from experiments.config_loader import load_experiment_config
from experiments.orchestrator import ExperimentError, run_experiment, validate_experiment_name
from experiments.reporting import RunRecord, build_aggregate_summary, write_aggregate_outputs


DEFAULT_SCENARIOS = {
    "proposed-baseline": "experiments/configs/proposed_baseline_long.yaml",
    "threshold-baseline": "experiments/configs/threshold_baseline_long.yaml",
    "reactive-baseline": "experiments/configs/reactive_baseline_long.yaml",
    "hpa-like-baseline": "experiments/configs/hpa_like_baseline_long.yaml",
    "predictive-only-baseline": "experiments/configs/predictive_only_baseline_long.yaml",
    "proposed-bursty": "experiments/configs/proposed_bursty_long.yaml",
    "proposed-mixed": "experiments/configs/proposed_mixed_long.yaml",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run repeated experiment scenarios and aggregate the results.")
    parser.add_argument("--batch-name", required=True, help="Batch name under results/<batch-name>/")
    parser.add_argument("--runs-per-scenario", type=int, default=3, help="Number of repeated runs per scenario")
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Keep running later scenarios even if one run fails.",
    )
    parser.add_argument(
        "--scenario",
        action="append",
        help="Scenario override in the form name=path/to/config.yaml. Can be provided multiple times.",
    )
    return parser


def resolve_scenarios(raw_values: list[str] | None) -> dict[str, Path]:
    if not raw_values:
        return {name: (ROOT_DIR / path).resolve() for name, path in DEFAULT_SCENARIOS.items()}

    scenarios: dict[str, Path] = {}
    for raw_value in raw_values:
        if "=" not in raw_value:
            raise ValueError("Each --scenario must look like name=path/to/config.yaml")
        name, raw_path = raw_value.split("=", 1)
        scenario_name = validate_experiment_name(name)
        candidate_path = Path(raw_path)
        if not candidate_path.is_absolute():
            candidate_path = ROOT_DIR / candidate_path
        scenarios[scenario_name] = candidate_path.resolve()
    return scenarios


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        batch_name = validate_experiment_name(args.batch_name)
        if args.runs_per_scenario < 1:
            raise ValueError("--runs-per-scenario must be greater than 0")
        scenarios = resolve_scenarios(args.scenario)
        batch_timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        batch_dir = ROOT_DIR / "results" / batch_name / batch_timestamp
        batch_dir.mkdir(parents=True, exist_ok=False)
        batch_log_path = batch_dir / "batch.log"

        records: list[RunRecord] = []
        _log(batch_log_path, f"Starting batch '{batch_name}' with {args.runs_per_scenario} runs per scenario.")
        for scenario_name, config_path in scenarios.items():
            config = load_experiment_config(config_path)
            for run_index in range(1, args.runs_per_scenario + 1):
                run_name = f"{batch_name}-{scenario_name}-r{run_index:02d}"
                _log(batch_log_path, f"Running scenario '{scenario_name}' as '{run_name}' using {config_path}.")
                try:
                    run_paths = run_experiment(
                        repo_root=ROOT_DIR,
                        config=config,
                        config_path=config_path,
                        experiment_name=run_name,
                    )
                    summary = _load_json(run_paths.summary_path)
                    _log(batch_log_path, f"Completed '{run_name}' with status {summary.get('status')}.")
                except Exception as error:
                    failed_run_dir = _latest_run_dir(ROOT_DIR / "results" / run_name)
                    summary = (
                        _load_json(failed_run_dir / "summary.json")
                        if failed_run_dir and (failed_run_dir / "summary.json").exists()
                        else {
                            "status": "failed",
                            "failure_reason": str(error),
                        }
                    )
                    run_paths = type("FallbackRunPaths", (), {"run_dir": failed_run_dir or (ROOT_DIR / "results" / run_name)})()
                    _log(batch_log_path, f"Run '{run_name}' failed: {summary.get('failure_reason') or error}")
                    if not args.continue_on_failure:
                        raise ExperimentError(
                            f"Batch stopped after failure in scenario '{scenario_name}' run {run_index}: {summary.get('failure_reason') or error}"
                        ) from error
                records.append(
                    RunRecord(
                        scenario=scenario_name,
                        run_name=run_name,
                        run_dir=run_paths.run_dir,
                        summary=summary,
                    )
                )

        aggregate_summary = build_aggregate_summary(batch_name=batch_name, records=records)
        write_aggregate_outputs(batch_dir=batch_dir, aggregate_summary=aggregate_summary)
        _log(batch_log_path, f"Batch '{batch_name}' finished. Aggregate outputs written to {batch_dir}.")
    except (ExperimentError, ValueError) as error:
        print(f"Batch run failed: {error}", file=sys.stderr)
        return 1
    except Exception as error:  # pragma: no cover - defensive CLI boundary
        print(f"Unexpected batch failure: {error}", file=sys.stderr)
        return 1

    print(f"Batch aggregate results written to {batch_dir}")
    return 0


def _load_json(path: Path) -> dict:
    import json

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _latest_run_dir(root: Path) -> Path | None:
    if not root.exists():
        return None
    run_dirs = [path for path in root.iterdir() if path.is_dir()]
    if not run_dirs:
        return None
    return sorted(run_dirs)[-1]


def _log(path: Path, message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    line = f"[{timestamp}] {message}"
    print(line)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


if __name__ == "__main__":
    raise SystemExit(main())

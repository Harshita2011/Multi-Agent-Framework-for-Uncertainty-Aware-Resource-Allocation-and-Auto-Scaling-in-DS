"""CLI for orchestrating Docker-first research experiments."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from experiments.config_loader import load_experiment_config
from experiments.orchestrator import ExperimentError, run_experiment, validate_experiment_name


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a Docker-first research experiment.")
    parser.add_argument("--name", required=True, help="Experiment name used under results/<experiment-name>/")
    parser.add_argument("--config", required=True, help="Path to the YAML experiment config")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        config_path = Path(args.config).resolve()
        experiment_name = validate_experiment_name(args.name)
        config = load_experiment_config(config_path)

        if config.experiment_name and config.experiment_name != experiment_name:
            print(
                f"Config experiment_name '{config.experiment_name}' overridden by CLI name '{experiment_name}'.",
                file=sys.stderr,
            )

        run_paths = run_experiment(
            repo_root=ROOT_DIR,
            config=config,
            config_path=config_path,
            experiment_name=experiment_name,
        )
    except (ExperimentError, ValueError) as error:
        print(f"Experiment failed: {error}", file=sys.stderr)
        return 1
    except Exception as error:  # pragma: no cover - defensive CLI boundary
        print(f"Unexpected experiment failure: {error}", file=sys.stderr)
        return 1

    print(f"Experiment results written to {run_paths.run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

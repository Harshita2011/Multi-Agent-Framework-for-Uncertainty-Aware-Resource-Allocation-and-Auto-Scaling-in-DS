"""Build a reproducibility bundle for paper submissions."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


ROOT_DIR = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create reproducibility package files.")
    parser.add_argument(
        "--output-dir",
        default="reproducibility",
        help="Output directory relative to repository root.",
    )
    parser.add_argument(
        "--include-config",
        action="append",
        default=[],
        help="Config paths to include in package manifest. Can be used multiple times.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_dir = (ROOT_DIR / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_commit": _capture(["git", "rev-parse", "HEAD"]),
        "git_status_short": _capture(["git", "status", "--short"]).splitlines(),
        "commands": {
            "single_run": "python experiments/run_experiment.py --name <name> --config <config-path>",
            "batch_run": "python experiments/run_batch.py --batch-name <name> --runs-per-scenario <n>",
            "conference_suite": (
                "python experiments/run_batch.py --batch-name conf-suite --runs-per-scenario 30 "
                "--scenario proposed=experiments/configs/proposed_baseline_long.yaml "
                "--scenario threshold=experiments/configs/threshold_baseline_long.yaml "
                "--scenario reactive=experiments/configs/reactive_baseline_long.yaml "
                "--scenario hpa=experiments/configs/hpa_like_baseline_long.yaml "
                "--scenario predictive=experiments/configs/predictive_only_baseline_long.yaml "
                "--scenario no-risk=experiments/configs/ablation_no_risk_baseline_long.yaml "
                "--scenario no-uncertainty=experiments/configs/ablation_no_uncertainty_baseline_long.yaml "
                "--scenario no-agents=experiments/configs/ablation_no_agents_baseline_long.yaml"
            ),
        },
    }

    configs = []
    for config_value in args.include_config:
        config_path = (ROOT_DIR / config_value).resolve()
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as handle:
                configs.append(
                    {
                        "path": str(config_path.relative_to(ROOT_DIR)),
                        "content": yaml.safe_load(handle) or {},
                    }
                )
    manifest["configs"] = configs

    with (output_dir / "manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)

    with (output_dir / "pip-freeze.txt").open("w", encoding="utf-8") as handle:
        freeze_output = _capture([sys.executable, "-m", "pip", "freeze"])
        handle.write(freeze_output + ("\n" if freeze_output else ""))

    with (output_dir / "reproduce.md").open("w", encoding="utf-8") as handle:
        handle.write(_build_reproduce_markdown(manifest))

    print(f"Reproducibility package written to {output_dir}")
    return 0


def _capture(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _build_reproduce_markdown(manifest: dict) -> str:
    lines = [
        "# Reproducibility Package",
        "",
        f"Generated at: `{manifest['generated_at']}`",
        "",
        "## Environment",
        "",
        f"- Python: `{manifest['python_version'].splitlines()[0]}`",
        f"- Platform: `{manifest['platform']}`",
        f"- Git commit: `{manifest.get('git_commit') or 'unknown'}`",
        "",
        "## Commands",
        "",
        f"- Single run: `{manifest['commands']['single_run']}`",
        f"- Batch run: `{manifest['commands']['batch_run']}`",
        f"- Conference suite: `{manifest['commands']['conference_suite']}`",
        "",
    ]
    if manifest.get("configs"):
        lines.extend(["## Included Configs", ""])
        for entry in manifest["configs"]:
            lines.append(f"- `{entry['path']}`")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

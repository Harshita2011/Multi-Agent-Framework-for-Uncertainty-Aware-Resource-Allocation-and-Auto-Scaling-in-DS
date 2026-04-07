"""Export latest batch outputs into the paper/ directory for submission workflows."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT_DIR / "results"
PAPER_ARTIFACTS_DIR = ROOT_DIR / "paper" / "artifacts"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Copy batch outputs into paper/artifacts with stable names for manuscript integration."
    )
    parser.add_argument(
        "--batch-name",
        required=True,
        help="Batch directory name under results/<batch-name>/",
    )
    parser.add_argument(
        "--timestamp",
        default=None,
        help="Optional batch timestamp. If omitted, latest timestamp under the batch is used.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PAPER_ARTIFACTS_DIR),
        help="Output directory for exported paper artifacts.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    batch_root = RESULTS_DIR / args.batch_name
    if not batch_root.exists():
        raise SystemExit(f"Batch not found: {batch_root}")

    if args.timestamp:
        batch_dir = batch_root / args.timestamp
        if not batch_dir.exists():
            raise SystemExit(f"Batch timestamp not found: {batch_dir}")
    else:
        candidates = sorted([path for path in batch_root.iterdir() if path.is_dir()])
        if not candidates:
            raise SystemExit(f"No timestamped runs found under: {batch_root}")
        batch_dir = candidates[-1]

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    required_files = [
        "aggregate_summary.json",
        "aggregate_table.csv",
        "aggregate_table.md",
        "aggregate_table.tex",
        "paper_summary.md",
        "pairwise_comparisons.json",
        "pairwise_comparisons.md",
        "step_metrics.svg",
        "batch.log",
    ]

    missing = [name for name in required_files if not (batch_dir / name).exists()]
    if missing:
        raise SystemExit(f"Batch is missing required files: {', '.join(missing)}")

    for file_name in required_files:
        source = batch_dir / file_name
        destination = output_dir / file_name
        shutil.copy2(source, destination)

    manifest = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "batch_name": args.batch_name,
        "batch_timestamp": batch_dir.name,
        "batch_dir": str(batch_dir),
        "output_dir": str(output_dir),
        "files": required_files,
    }
    with (output_dir / "export_manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)

    _write_publication_notes(output_dir, manifest)
    print(f"Publication artifacts exported to {output_dir}")
    return 0


def _write_publication_notes(output_dir: Path, manifest: dict[str, object]) -> None:
    lines = [
        "# Publication Artifact Notes",
        "",
        f"- Exported at: `{manifest['exported_at']}`",
        f"- Source batch: `{manifest['batch_name']}/{manifest['batch_timestamp']}`",
        "",
        "## Included Files",
        "",
    ]
    for file_name in manifest["files"]:
        lines.append(f"- `{file_name}`")
    lines.extend(
        [
            "",
            "## Suggested Manuscript Mapping",
            "",
            "- Main quantitative table: `aggregate_table.tex`",
            "- Statistical appendix: `pairwise_comparisons.md`",
            "- Narrative results section draft: `paper_summary.md`",
            "- Figure candidate: `step_metrics.svg`",
        ]
    )
    with (output_dir / "PUBLICATION_NOTES.md").open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())

"""Aggregation and reporting helpers for experiment batches."""

from __future__ import annotations

import csv
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev
from typing import Any


@dataclass(frozen=True)
class RunRecord:
    """Single experiment summary plus provenance."""

    scenario: str
    run_name: str
    run_dir: Path
    summary: dict[str, Any]


def build_aggregate_summary(batch_name: str, records: list[RunRecord]) -> dict[str, Any]:
    """Aggregate per-run summaries into scenario-level statistics."""

    grouped: dict[str, list[RunRecord]] = defaultdict(list)
    for record in records:
        grouped[record.scenario].append(record)

    scenarios: dict[str, Any] = {}
    overall_runs_requested = 0
    overall_runs_succeeded = 0
    overall_runs_failed = 0
    for scenario, scenario_records in grouped.items():
        successful = [record for record in scenario_records if record.summary.get("status") == "success"]
        failed = [record for record in scenario_records if record.summary.get("status") != "success"]
        overall_runs_requested += len(scenario_records)
        overall_runs_succeeded += len(successful)
        overall_runs_failed += len(failed)

        metrics = {
            "final_rmse": [float(record.summary["final_rmse"]) for record in successful if record.summary["final_rmse"] is not None],
            "average_utilization": [float(record.summary["average_utilization"]) for record in successful if record.summary["average_utilization"] is not None],
            "average_prediction": [float(record.summary["average_prediction"]) for record in successful if record.summary["average_prediction"] is not None],
            "average_risk": [float(record.summary["average_risk"]) for record in successful if record.summary["average_risk"] is not None],
            "p95_utilization": [float(record.summary["p95_utilization"]) for record in successful if record.summary.get("p95_utilization") is not None],
            "sla_violation_rate": [float(record.summary["sla_violation_rate"]) for record in successful if record.summary.get("sla_violation_rate") is not None],
            "control_loop_latency_ms": [float(record.summary["control_loop_latency_ms"]) for record in successful if record.summary.get("control_loop_latency_ms") is not None],
            "throughput_proxy": [float(record.summary["throughput_proxy"]) for record in successful if record.summary.get("throughput_proxy") is not None],
            "cost_proxy": [float(record.summary["cost_proxy"]) for record in successful if record.summary.get("cost_proxy") is not None],
            "action_churn_rate": [float(record.summary["action_churn_rate"]) for record in successful if record.summary.get("action_churn_rate") is not None],
        }
        action_counter: Counter[str] = Counter()
        for record in successful:
            action_counter.update(record.summary.get("action_counts", {}))
        dominant_action = action_counter.most_common(1)[0][0] if action_counter else None
        policy = next(
            (record.summary.get("policy") for record in scenario_records if record.summary.get("policy")),
            None,
        )

        scenarios[scenario] = {
            "runs_requested": len(scenario_records),
            "runs_succeeded": len(successful),
            "runs_failed": len(failed),
            "success_rate": round(len(successful) / len(scenario_records), 4) if scenario_records else None,
            "policy": policy,
            "metric_samples": metrics,
            "metrics": {
                key: _describe(values)
                for key, values in metrics.items()
            },
            "action_totals": dict(action_counter),
            "dominant_action": dominant_action,
            "run_directories": [str(record.run_dir) for record in scenario_records],
            "failed_runs": [
                {
                    "run_name": record.run_name,
                    "failure_reason": record.summary.get("failure_reason"),
                }
                for record in failed
            ],
        }

    return {
        "batch_name": batch_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runs_requested": overall_runs_requested,
        "runs_succeeded": overall_runs_succeeded,
        "runs_failed": overall_runs_failed,
        "scenarios": scenarios,
    }


def write_aggregate_outputs(batch_dir: Path, aggregate_summary: dict[str, Any]) -> None:
    """Persist JSON, CSV, and Markdown aggregate views."""

    json_path = batch_dir / "aggregate_summary.json"
    csv_path = batch_dir / "aggregate_table.csv"
    markdown_path = batch_dir / "aggregate_table.md"
    latex_path = batch_dir / "aggregate_table.tex"
    narrative_path = batch_dir / "paper_summary.md"
    pairwise_json_path = batch_dir / "pairwise_comparisons.json"
    pairwise_markdown_path = batch_dir / "pairwise_comparisons.md"

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(aggregate_summary, handle, indent=2)

    pairwise_comparisons = _build_pairwise_comparisons(aggregate_summary)
    with pairwise_json_path.open("w", encoding="utf-8") as handle:
        json.dump(pairwise_comparisons, handle, indent=2)

    rows = []
    for scenario, details in aggregate_summary["scenarios"].items():
        rows.append(
            {
                "scenario": scenario,
                "runs_requested": details["runs_requested"],
                "runs_succeeded": details["runs_succeeded"],
                "runs_failed": details["runs_failed"],
                "success_rate": details["success_rate"],
                "policy": details["policy"],
                "rmse_mean": details["metrics"]["final_rmse"]["mean"],
                "rmse_std": details["metrics"]["final_rmse"]["stddev"],
                "rmse_ci95": details["metrics"]["final_rmse"]["ci95"],
                "utilization_mean": details["metrics"]["average_utilization"]["mean"],
                "utilization_std": details["metrics"]["average_utilization"]["stddev"],
                "utilization_ci95": details["metrics"]["average_utilization"]["ci95"],
                "prediction_mean": details["metrics"]["average_prediction"]["mean"],
                "prediction_std": details["metrics"]["average_prediction"]["stddev"],
                "prediction_ci95": details["metrics"]["average_prediction"]["ci95"],
                "risk_mean": details["metrics"]["average_risk"]["mean"],
                "risk_std": details["metrics"]["average_risk"]["stddev"],
                "risk_ci95": details["metrics"]["average_risk"]["ci95"],
                "p95_util_mean": details["metrics"]["p95_utilization"]["mean"],
                "sla_violation_rate_mean": details["metrics"]["sla_violation_rate"]["mean"],
                "control_loop_latency_ms_mean": details["metrics"]["control_loop_latency_ms"]["mean"],
                "throughput_proxy_mean": details["metrics"]["throughput_proxy"]["mean"],
                "cost_proxy_mean": details["metrics"]["cost_proxy"]["mean"],
                "action_churn_rate_mean": details["metrics"]["action_churn_rate"]["mean"],
                "dominant_action": details["dominant_action"],
                "action_totals": json.dumps(details["action_totals"]),
            }
        )

    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    markdown_lines = [
        "| Scenario | Policy | Runs | Success | Fail | Success Rate | RMSE (Mean +- Std, CI95) | Utilization (Mean +- Std, CI95) | Prediction (Mean +- Std, CI95) | Risk (Mean +- Std, CI95) | P95 Util | SLA Viol. Rate | Ctrl Latency ms | Throughput Proxy | Cost Proxy | Action Churn | Dominant Action | Actions |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        markdown_lines.append(
            f"| {row['scenario']} | {row['policy']} | {row['runs_requested']} | {row['runs_succeeded']} | {row['runs_failed']} | "
            f"{_format_percent(row['success_rate'])} | "
            f"{_format_metric(row['rmse_mean'], row['rmse_std'], row['rmse_ci95'])} | "
            f"{_format_metric(row['utilization_mean'], row['utilization_std'], row['utilization_ci95'])} | "
            f"{_format_metric(row['prediction_mean'], row['prediction_std'], row['prediction_ci95'])} | "
            f"{_format_metric(row['risk_mean'], row['risk_std'], row['risk_ci95'])} | "
            f"{row['p95_util_mean']} | "
            f"{_format_percent(row['sla_violation_rate_mean'])} | "
            f"{row['control_loop_latency_ms_mean']} | "
            f"{row['throughput_proxy_mean']} | "
            f"{row['cost_proxy_mean']} | "
            f"{row['action_churn_rate_mean']} | "
            f"{row['dominant_action']} | `{row['action_totals']}` |"
        )

    with markdown_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(markdown_lines) + "\n")

    latex_lines = [
        "\\begin{table}[h]",
        "\\centering",
        "\\caption{Batch experiment results for the uncertainty-aware auto-scaling framework.}",
        "\\label{tab:batch-results}",
        "\\begin{tabular}{llccccc}",
        "\\hline",
        "Scenario & Policy & Runs & Success Rate & RMSE & Utilization & Prediction & Risk \\\\",
        "\\hline",
    ]
    for row in rows:
        latex_lines.append(
            f"{row['scenario']} & {row['policy']} & {row['runs_requested']} & {_format_percent(row['success_rate'], latex=True)} & "
            f"{_format_metric(row['rmse_mean'], row['rmse_std'], row['rmse_ci95'], latex=True)} & "
            f"{_format_metric(row['utilization_mean'], row['utilization_std'], row['utilization_ci95'], latex=True)} & "
            f"{_format_metric(row['prediction_mean'], row['prediction_std'], row['prediction_ci95'], latex=True)} & "
            f"{_format_metric(row['risk_mean'], row['risk_std'], row['risk_ci95'], latex=True)} \\\\"
        )
    latex_lines.extend(["\\hline", "\\end{tabular}", "\\end{table}"])
    with latex_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(latex_lines) + "\n")

    with narrative_path.open("w", encoding="utf-8") as handle:
        handle.write(_build_narrative(aggregate_summary, rows, pairwise_comparisons))

    with pairwise_markdown_path.open("w", encoding="utf-8") as handle:
        handle.write(_build_pairwise_markdown(pairwise_comparisons))

    _write_step_plots(batch_dir, aggregate_summary)


def _describe(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"mean": None, "stddev": None, "ci95": None}
    if len(values) == 1:
        return {"mean": round(values[0], 4), "stddev": 0.0, "ci95": 0.0}
    sample_std = stdev(values)
    ci95 = 1.96 * sample_std / math.sqrt(len(values))
    return {
        "mean": round(mean(values), 4),
        "stddev": round(sample_std, 4),
        "ci95": round(ci95, 4),
    }


def _format_plus_minus(mean_value: float | None, std_value: float | None, latex: bool = False) -> str:
    if mean_value is None:
        return "n/a"
    if std_value is None:
        return f"{mean_value}"
    if latex:
        return f"{mean_value} $\\\\pm$ {std_value}"
    return f"{mean_value} +- {std_value}"


def _format_metric(mean_value: float | None, std_value: float | None, ci95: float | None, latex: bool = False) -> str:
    if mean_value is None:
        return "n/a"
    ci_fragment = "n/a" if ci95 is None else str(ci95)
    if latex:
        return f"{_format_plus_minus(mean_value, std_value, latex=True)}, CI95={ci_fragment}"
    return f"{_format_plus_minus(mean_value, std_value)}, CI95={ci_fragment}"


def _format_percent(value: float | None, latex: bool = False) -> str:
    if value is None:
        return "n/a"
    suffix = "\\%" if latex else "%"
    return f"{round(value * 100, 1)}{suffix}"


def _build_narrative(
    aggregate_summary: dict[str, Any],
    rows: list[dict[str, Any]],
    pairwise_comparisons: dict[str, Any],
) -> str:
    lines = [
        "# Paper Summary",
        "",
        f"Batch `{aggregate_summary['batch_name']}` produced {aggregate_summary['runs_succeeded']} successful runs out of {aggregate_summary['runs_requested']}.",
        "",
    ]
    if rows:
        strongest_prediction = max(rows, key=lambda row: row["prediction_mean"] if row["prediction_mean"] is not None else float("-inf"))
        lowest_risk = min(rows, key=lambda row: row["risk_mean"] if row["risk_mean"] is not None else float("inf"))
        lines.extend(
            [
                f"The highest mean prediction was observed in `{strongest_prediction['scenario']}` at {_format_plus_minus(strongest_prediction['prediction_mean'], strongest_prediction['prediction_std'])}.",
                f"The lowest mean risk was observed in `{lowest_risk['scenario']}` at {_format_plus_minus(lowest_risk['risk_mean'], lowest_risk['risk_std'])}.",
                "",
                "## Scenario Notes",
                "",
            ]
        )
        for row in rows:
            lines.append(
                f"- `{row['scenario']}` using `{row['policy']}`: success rate {_format_percent(row['success_rate'])}, "
                f"RMSE {_format_metric(row['rmse_mean'], row['rmse_std'], row['rmse_ci95'])}, "
                f"utilization {_format_metric(row['utilization_mean'], row['utilization_std'], row['utilization_ci95'])}, "
                f"dominant action `{row['dominant_action']}`."
            )
    highlights = _pairwise_highlights(pairwise_comparisons)
    if highlights:
        lines.extend(["", "## Pairwise Notes", ""])
        lines.extend(f"- {item}" for item in highlights)
    return "\n".join(lines) + "\n"


def _build_pairwise_comparisons(aggregate_summary: dict[str, Any]) -> dict[str, Any]:
    scenarios = aggregate_summary["scenarios"]
    metrics = [
        "final_rmse",
        "average_utilization",
        "average_prediction",
        "average_risk",
        "p95_utilization",
        "sla_violation_rate",
        "control_loop_latency_ms",
        "throughput_proxy",
        "cost_proxy",
        "action_churn_rate",
    ]
    comparisons: list[dict[str, Any]] = []

    for left_name, right_name in itertools.combinations(sorted(scenarios), 2):
        left = scenarios[left_name]
        right = scenarios[right_name]
        metric_results: dict[str, Any] = {}
        for metric_name in metrics:
            left_values = [float(value) for value in left["metric_samples"].get(metric_name, [])]
            right_values = [float(value) for value in right["metric_samples"].get(metric_name, [])]
            metric_results[metric_name] = _compare_metric(left_values, right_values)
        comparisons.append(
            {
                "left_scenario": left_name,
                "left_policy": left.get("policy"),
                "right_scenario": right_name,
                "right_policy": right.get("policy"),
                "metrics": metric_results,
            }
        )

    _apply_holm_bonferroni(comparisons)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "multiple_comparison_correction": "holm-bonferroni",
        "comparisons": comparisons,
    }


def _compare_metric(left_values: list[float], right_values: list[float]) -> dict[str, Any]:
    if not left_values or not right_values:
        return {
            "left_mean": None,
            "right_mean": None,
            "mean_difference": None,
            "bootstrap_ci95": [None, None],
            "cliffs_delta": None,
            "cliffs_delta_magnitude": None,
            "permutation_pvalue": None,
            "permutation_pvalue_holm": None,
            "reject_null_holm_alpha_0_05": None,
        }

    left_mean = mean(left_values)
    right_mean = mean(right_values)
    mean_difference = left_mean - right_mean
    ci_low, ci_high = _bootstrap_difference_ci(left_values, right_values)
    return {
        "left_mean": round(left_mean, 4),
        "right_mean": round(right_mean, 4),
        "mean_difference": round(mean_difference, 4),
        "bootstrap_ci95": [round(ci_low, 4), round(ci_high, 4)],
        "cliffs_delta": round(_cliffs_delta(left_values, right_values), 4),
        "cliffs_delta_magnitude": _cliffs_delta_magnitude(_cliffs_delta(left_values, right_values)),
        "permutation_pvalue": round(_permutation_pvalue(left_values, right_values), 4),
        "permutation_pvalue_holm": None,
        "reject_null_holm_alpha_0_05": None,
    }


def _bootstrap_difference_ci(left_values: list[float], right_values: list[float], samples: int = 2000) -> tuple[float, float]:
    rng = random.Random(20260331)
    differences: list[float] = []
    for _ in range(samples):
        left_sample = [left_values[rng.randrange(len(left_values))] for _ in range(len(left_values))]
        right_sample = [right_values[rng.randrange(len(right_values))] for _ in range(len(right_values))]
        differences.append(mean(left_sample) - mean(right_sample))
    differences.sort()
    lower_index = int(0.025 * (samples - 1))
    upper_index = int(0.975 * (samples - 1))
    return differences[lower_index], differences[upper_index]


def _permutation_pvalue(left_values: list[float], right_values: list[float], permutations: int = 4000) -> float:
    observed = abs(mean(left_values) - mean(right_values))
    combined = list(left_values) + list(right_values)
    left_size = len(left_values)
    rng = random.Random(20260331)
    exceedances = 1
    for _ in range(permutations):
        shuffled = combined[:]
        rng.shuffle(shuffled)
        difference = abs(mean(shuffled[:left_size]) - mean(shuffled[left_size:]))
        if difference >= observed:
            exceedances += 1
    return exceedances / (permutations + 1)


def _cliffs_delta(left_values: list[float], right_values: list[float]) -> float:
    wins = 0
    losses = 0
    for left_value in left_values:
        for right_value in right_values:
            if left_value > right_value:
                wins += 1
            elif left_value < right_value:
                losses += 1
    total = len(left_values) * len(right_values)
    if total == 0:
        return 0.0
    return (wins - losses) / total


def _build_pairwise_markdown(pairwise_comparisons: dict[str, Any]) -> str:
    lines = [
        "# Pairwise Comparisons",
        "",
        "Permutation p-values and bootstrap confidence intervals are included to make the batch outputs easier to defend in a report.",
        "",
    ]
    for comparison in pairwise_comparisons["comparisons"]:
        lines.append(
            f"## {comparison['left_scenario']} vs {comparison['right_scenario']}"
        )
        lines.append("")
        lines.append("| Metric | Left Mean | Right Mean | Mean Diff | CI95 | Cliff's Delta | Magnitude | Permutation p | Holm p | Reject H0 @0.05 |")
        lines.append("|---|---:|---:|---:|---|---:|---|---:|---:|---|")
        for metric_name, metric_result in comparison["metrics"].items():
            ci = metric_result["bootstrap_ci95"]
            lines.append(
                f"| {metric_name} | {metric_result['left_mean']} | {metric_result['right_mean']} | "
                f"{metric_result['mean_difference']} | [{ci[0]}, {ci[1]}] | "
                f"{metric_result['cliffs_delta']} | {metric_result['cliffs_delta_magnitude']} | "
                f"{metric_result['permutation_pvalue']} | {metric_result['permutation_pvalue_holm']} | "
                f"{metric_result['reject_null_holm_alpha_0_05']} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def _pairwise_highlights(pairwise_comparisons: dict[str, Any]) -> list[str]:
    highlights: list[str] = []
    for comparison in pairwise_comparisons["comparisons"]:
        risk_result = comparison["metrics"]["average_risk"]
        if risk_result["mean_difference"] is None:
            continue
        if risk_result["reject_null_holm_alpha_0_05"]:
            better = comparison["left_scenario"] if risk_result["mean_difference"] < 0 else comparison["right_scenario"]
            highlights.append(
                f"`{better}` shows a lower average risk in the {comparison['left_scenario']} vs {comparison['right_scenario']} comparison "
                f"(Holm-corrected p={risk_result['permutation_pvalue_holm']}, Cliff's delta={risk_result['cliffs_delta']})."
            )
    return highlights


def _apply_holm_bonferroni(comparisons: list[dict[str, Any]], alpha: float = 0.05) -> None:
    tests: list[tuple[float, dict[str, Any]]] = []
    for comparison in comparisons:
        for metric_result in comparison["metrics"].values():
            pvalue = metric_result.get("permutation_pvalue")
            if pvalue is None:
                continue
            tests.append((float(pvalue), metric_result))

    if not tests:
        return

    sorted_tests = sorted(tests, key=lambda item: item[0])
    m = len(sorted_tests)
    # Holm step-down adjusted p-values.
    adjusted_values: list[float] = [0.0] * m
    running_max = 0.0
    for index, (pvalue, _) in enumerate(sorted_tests):
        adjusted = (m - index) * pvalue
        running_max = max(running_max, adjusted)
        adjusted_values[index] = min(1.0, running_max)

    for index, (_, metric_result) in enumerate(sorted_tests):
        adjusted = round(adjusted_values[index], 4)
        metric_result["permutation_pvalue_holm"] = adjusted
        metric_result["reject_null_holm_alpha_0_05"] = adjusted <= alpha


def _cliffs_delta_magnitude(delta: float) -> str:
    absolute = abs(delta)
    if absolute < 0.147:
        return "negligible"
    if absolute < 0.33:
        return "small"
    if absolute < 0.474:
        return "medium"
    return "large"


def _write_step_plots(batch_dir: Path, aggregate_summary: dict[str, Any]) -> None:
    scenario_series: dict[str, dict[str, list[float]]] = {}
    for scenario, details in aggregate_summary["scenarios"].items():
        successful_run_dirs = [Path(path) for path in details["run_directories"]]
        per_metric_steps: dict[str, list[list[float]]] = {
            "workload": [],
            "prediction": [],
            "risk_score": [],
            "utilization": [],
        }
        for run_dir in successful_run_dirs:
            step_log_path = run_dir / "step_logs.csv"
            if not step_log_path.exists():
                continue
            with step_log_path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                step_rows = list(reader)
            if not step_rows:
                continue
            for metric in per_metric_steps:
                per_metric_steps[metric].append([float(row[metric]) for row in step_rows])

        scenario_series[scenario] = {
            metric: _mean_per_step(runs)
            for metric, runs in per_metric_steps.items()
            if runs
        }

    if not scenario_series:
        return

    svg_path = batch_dir / "step_metrics.svg"
    width = 1000
    height = 760
    panel_width = 430
    panel_height = 250
    margin_left = 60
    margin_top = 40
    gap_x = 40
    gap_y = 70
    metrics = [
        ("workload", "Workload"),
        ("prediction", "Prediction"),
        ("risk_score", "Risk"),
        ("utilization", "Utilization"),
    ]
    colors = ["#0b6e4f", "#c84c09", "#355c7d", "#8f2d56", "#6c5b7b"]
    scenario_colors = {scenario: colors[index % len(colors)] for index, scenario in enumerate(sorted(scenario_series))}

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="40" y="28" font-family="Segoe UI, Arial, sans-serif" font-size="22" fill="#222">Batch Step Metrics</text>',
    ]

    for metric_index, (metric_key, metric_label) in enumerate(metrics):
        col = metric_index % 2
        row = metric_index // 2
        origin_x = margin_left + col * (panel_width + gap_x)
        origin_y = margin_top + row * (panel_height + gap_y)
        lines.extend(
            [
                f'<rect x="{origin_x}" y="{origin_y}" width="{panel_width}" height="{panel_height}" fill="none" stroke="#cccccc" stroke-width="1"/>',
                f'<text x="{origin_x}" y="{origin_y - 10}" font-family="Segoe UI, Arial, sans-serif" font-size="16" fill="#222">{metric_label}</text>',
            ]
        )

        plot_x = origin_x + 40
        plot_y = origin_y + 20
        plot_width = panel_width - 60
        plot_height = panel_height - 50

        lines.extend(
            [
                f'<line x1="{plot_x}" y1="{plot_y + plot_height}" x2="{plot_x + plot_width}" y2="{plot_y + plot_height}" stroke="#999" stroke-width="1"/>',
                f'<line x1="{plot_x}" y1="{plot_y}" x2="{plot_x}" y2="{plot_y + plot_height}" stroke="#999" stroke-width="1"/>',
            ]
        )

        max_steps = max((len(series.get(metric_key, [])) for series in scenario_series.values()), default=1)
        for scenario, series in sorted(scenario_series.items()):
            values = series.get(metric_key, [])
            if not values:
                continue
            points: list[str] = []
            for index, value in enumerate(values):
                x = plot_x if max_steps == 1 else plot_x + (index / (max_steps - 1)) * plot_width
                y = plot_y + plot_height - (value * plot_height)
                points.append(f"{round(x, 2)},{round(y, 2)}")
            lines.append(
                f'<polyline fill="none" stroke="{scenario_colors[scenario]}" stroke-width="2.5" points="{" ".join(points)}"/>'
            )

        for tick in range(6):
            value = tick / 5
            y = plot_y + plot_height - (value * plot_height)
            lines.append(
                f'<text x="{plot_x - 32}" y="{y + 4}" font-family="Segoe UI, Arial, sans-serif" font-size="11" fill="#555">{round(value, 1)}</text>'
            )

        if max_steps > 1:
            for step_number in range(max_steps):
                x = plot_x + (step_number / (max_steps - 1)) * plot_width
                lines.append(
                    f'<text x="{x - 4}" y="{plot_y + plot_height + 18}" font-family="Segoe UI, Arial, sans-serif" font-size="11" fill="#555">{step_number + 1}</text>'
                )

    legend_y = height - 30
    legend_x = 60
    for scenario in sorted(scenario_series):
        color = scenario_colors[scenario]
        lines.append(f'<rect x="{legend_x}" y="{legend_y - 12}" width="18" height="8" fill="{color}"/>')
        lines.append(f'<text x="{legend_x + 26}" y="{legend_y - 4}" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#222">{scenario}</text>')
        legend_x += 170

    lines.append("</svg>")
    with svg_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def _mean_per_step(runs: list[list[float]]) -> list[float]:
    if not runs:
        return []
    step_count = min(len(run) for run in runs)
    output: list[float] = []
    for step_index in range(step_count):
        values = [run[step_index] for run in runs]
        output.append(round(sum(values) / len(values), 4))
    return output

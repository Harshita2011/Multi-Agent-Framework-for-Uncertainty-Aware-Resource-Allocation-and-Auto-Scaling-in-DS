# Results

This file summarizes the strongest validated experiment outputs for the Docker-first research workflow.

## Final Policy Comparison

- Batch name: `policy-compare-10b`
- Generated at: `2026-03-29T17:41:58.648667+00:00`
- Runs requested: `30`
- Runs succeeded: `30`
- Runs failed: `0`
- Timesteps per run: `20`

Primary source files:

- [aggregate_summary.json](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/results/policy-compare-10b/20260329T173343Z/aggregate_summary.json)
- [aggregate_table.md](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/results/policy-compare-10b/20260329T173343Z/aggregate_table.md)
- [aggregate_table.tex](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/results/policy-compare-10b/20260329T173343Z/aggregate_table.tex)
- [paper_summary.md](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/results/policy-compare-10b/20260329T173343Z/paper_summary.md)
- [step_metrics.svg](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/results/policy-compare-10b/20260329T173343Z/step_metrics.svg)

## Aggregate Table

| Scenario | Policy | Runs | Success | Fail | Success Rate | RMSE (Mean +- Std, CI95) | Utilization (Mean +- Std, CI95) | Prediction (Mean +- Std, CI95) | Risk (Mean +- Std, CI95) | Dominant Action | Actions |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| proposed | proposed | 10 | 10 | 0 | 100.0% | 0.058 +- 0.014, CI95=0.0087 | 0.5976 +- 0.0438, CI95=0.0271 | 0.5367 +- 0.0892, CI95=0.0553 | 0.3791 +- 0.0354, CI95=0.022 | hold | `{"hold": 170, "scale_down": 6, "scale_up": 24}` |
| threshold | threshold | 10 | 10 | 0 | 100.0% | 0.053 +- 0.0095, CI95=0.0059 | 0.599 +- 0.0384, CI95=0.0238 | 0.5398 +- 0.1211, CI95=0.0751 | 0.3817 +- 0.028, CI95=0.0173 | hold | `{"hold": 199, "scale_up": 1}` |
| reactive | reactive | 10 | 10 | 0 | 100.0% | 0.061 +- 0.016, CI95=0.0099 | 0.6065 +- 0.0452, CI95=0.028 | 0.5131 +- 0.1387, CI95=0.086 | 0.387 +- 0.0331, CI95=0.0205 | hold | `{"hold": 200}` |

## Key Findings

- All 30 runs completed successfully, so the experiment workflow remained stable across repeated policy comparisons.
- The `proposed` policy achieved the lowest mean risk (`0.3791`) among the three policies.
- The `proposed` policy was the only policy to show sustained adaptive behavior, with both `scale_up` and `scale_down` actions across repeated runs.
- The `threshold` and `reactive` baselines were far more conservative, remaining almost entirely at `hold`.
- Confidence intervals are now based on 10 repeated runs per policy, which makes the results materially stronger than the earlier 1-run and 2-run comparisons.

## Interpretation

The policy comparison suggests that the uncertainty-aware proposed approach is more dynamically responsive than the threshold-only and reactive baselines. While the average RMSE and utilization values are broadly similar across policies in this synthetic environment, the action profiles differ sharply: the proposed policy adapts with both upward and downward scaling, whereas the baseline policies remain nearly static. In this experiment set, the proposed policy also produced the lowest mean risk, which supports the claim that combining prediction and uncertainty can guide more nuanced control behavior than simple threshold or reactive rules alone.

## Scenario Batch Reference

The workload-scenario comparison remains available for the bursty, baseline, and mixed regimes:

- [aggregate_summary.json](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/results/paper-batch/20260329T170629Z/aggregate_summary.json)
- [aggregate_table.md](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/results/paper-batch/20260329T170629Z/aggregate_table.md)

That batch showed:

- `bursty` produced the highest mean prediction and utilization
- `mixed` produced the lowest mean prediction and repeated `scale_down`
- `baseline` remained comparatively stable and was dominated by `hold`

## Notes

- The main reported result should now be the 30-run policy batch under `results/policy-compare-10b/20260329T173343Z/`.
- For direct LaTeX inclusion, use [aggregate_table.tex](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/results/policy-compare-10b/20260329T173343Z/aggregate_table.tex).
- For the generated narrative summary, use [paper_summary.md](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/results/policy-compare-10b/20260329T173343Z/paper_summary.md).
- For the generated visual comparison, use [step_metrics.svg](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/results/policy-compare-10b/20260329T173343Z/step_metrics.svg).

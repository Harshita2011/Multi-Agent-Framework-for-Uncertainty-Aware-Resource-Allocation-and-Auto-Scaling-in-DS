# Publication Checklist

Use this checklist before submitting to a conference or journal.

## Data and Traces

1. At least one experiment set uses replayed trace data (`workload_source: replay`).
2. Trace provenance is documented (source, date, preprocessing).
3. Trace normalization and clipping method are explicitly described.

## Experimental Design

1. Run count per scenario is at least 30 for headline comparisons.
2. Baseline breadth includes at least `threshold`, `reactive`, `hpa-like`, and `predictive-only`.
3. Ablation coverage includes `proposed-no-risk`, `proposed-no-uncertainty`, and `proposed-no-agents`.

## Statistical Rigor

1. Pairwise comparisons include permutation p-values.
2. Multiple comparisons are corrected via Holm-Bonferroni.
3. Effect sizes are reported using Cliff's delta and magnitude labels.
4. Bootstrap confidence intervals are reported for mean differences.

## Metrics

1. Core metrics: RMSE, average utilization, average prediction, average risk.
2. Extended metrics: p95 utilization, SLA violation rate, control-loop latency, throughput proxy, cost proxy, action churn.
3. Action distributions are reported for all policies.

## Reproducibility

1. `provenance.json` is present for each run.
2. `workload_trace.json` is present for each run.
3. Reproducibility package includes `manifest.json`, `pip-freeze.txt`, and `reproduce.md`.
4. Exact commands used to generate headline tables are included in the paper appendix.

## Manuscript Quality

1. IEEE table/figure labels match generated artifacts.
2. Claims map directly to result files in `results/`.
3. Limitations and threats to validity are explicit.
4. Bibliography is complete and uses scholarly sources.

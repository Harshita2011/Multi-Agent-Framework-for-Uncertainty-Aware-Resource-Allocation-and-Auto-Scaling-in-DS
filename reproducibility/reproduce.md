# Reproducibility Package

Generated at: `2026-04-07T17:08:42.292257+00:00`

## Environment

- Python: `3.11.0 (main, Oct 24 2022, 18:26:48) [MSC v.1933 64 bit (AMD64)]`
- Platform: `Windows-10-10.0.26200-SP0`
- Git commit: `24f4c263c879be74b752208f226622044e998dca`

## Commands

- Single run: `python experiments/run_experiment.py --name <name> --config <config-path>`
- Batch run: `python experiments/run_batch.py --batch-name <name> --runs-per-scenario <n>`
- Conference suite: `python experiments/run_batch.py --batch-name conf-suite --runs-per-scenario 30 --scenario proposed=experiments/configs/proposed_baseline_long.yaml --scenario threshold=experiments/configs/threshold_baseline_long.yaml --scenario reactive=experiments/configs/reactive_baseline_long.yaml --scenario hpa=experiments/configs/hpa_like_baseline_long.yaml --scenario predictive=experiments/configs/predictive_only_baseline_long.yaml --scenario no-risk=experiments/configs/ablation_no_risk_baseline_long.yaml --scenario no-uncertainty=experiments/configs/ablation_no_uncertainty_baseline_long.yaml --scenario no-agents=experiments/configs/ablation_no_agents_baseline_long.yaml`

## Included Configs

- `experiments\configs\proposed_baseline_long.yaml`
- `experiments\configs\replay_trace_long.yaml`

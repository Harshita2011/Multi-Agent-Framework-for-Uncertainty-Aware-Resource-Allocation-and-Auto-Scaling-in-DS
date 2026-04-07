# Trace Replay Files

This folder contains replayable workload traces for `workload_source: replay`.

- `trace_replay_sample.csv`: small normalized trace for pipeline validation.

For conference/journal-grade studies, replace the sample with a real trace extract and point configs to that file using `workload_trace_path`.

Accepted trace formats:

1. `.csv` with a `workload` column (preferred)
2. `.json` list or `{ "trace": [...] }`
3. `.yaml` list or `{ trace: [...] }`

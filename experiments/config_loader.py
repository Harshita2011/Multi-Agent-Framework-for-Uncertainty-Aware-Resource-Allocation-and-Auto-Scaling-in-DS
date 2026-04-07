"""Configuration loading for Docker-first experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import csv
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RiskInputStrategy:
    """How node metrics should be mapped into the risk service request."""

    cpu_source: str = "average"
    memory_source: str = "average"
    uncertainty_source: str = "prediction"


@dataclass(frozen=True)
class ExperimentConfig:
    """Validated experiment configuration."""

    experiment_name: str | None
    timesteps: int
    step_sleep_seconds: float = 0.0
    target_nodes: list[str] = field(default_factory=lambda: ["node-1", "node-2"])
    history_seed: list[float] = field(default_factory=lambda: [0.5, 0.6, 0.7])
    workload_mode: str = "baseline"
    workload_source: str = "service"
    trace_seed: int = 20260331
    workload_trace: list[float] | None = None
    workload_trace_path: str | None = None
    policy: str = "proposed"
    risk_inputs: RiskInputStrategy = field(default_factory=RiskInputStrategy)
    summary_metrics: list[str] = field(
        default_factory=lambda: [
            "final_rmse",
            "average_utilization",
            "action_counts",
            "average_prediction",
            "average_risk",
            "p95_utilization",
            "sla_violation_rate",
            "control_loop_latency_ms",
            "throughput_proxy",
            "cost_proxy",
        ]
    )
    service_urls: dict[str, str] = field(
        default_factory=lambda: {
            "node-1": "http://127.0.0.1:8001",
            "node-2": "http://127.0.0.1:8002",
            "workload": "http://127.0.0.1:8003",
            "prediction": "http://127.0.0.1:8004",
            "risk": "http://127.0.0.1:8005",
            "agent": "http://127.0.0.1:8006",
            "resource": "http://127.0.0.1:8007",
            "allocation": "http://127.0.0.1:8008",
            "coordinator": "http://127.0.0.1:8009",
            "execution": "http://127.0.0.1:8010",
            "evaluation": "http://127.0.0.1:8011",
        }
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation for persistence."""

        return asdict(self)


def load_experiment_config(path: Path) -> ExperimentConfig:
    """Load and validate an experiment config from YAML."""

    if not path.exists():
        raise ValueError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}

    if not isinstance(payload, dict):
        raise ValueError("Config root must be a YAML object")

    timesteps = payload.get("timesteps")
    if not isinstance(timesteps, int) or timesteps < 1:
        raise ValueError("timesteps must be an integer greater than 0")

    step_sleep_seconds = float(payload.get("step_sleep_seconds", 0.0))
    if step_sleep_seconds < 0:
        raise ValueError("step_sleep_seconds must be non-negative")

    target_nodes = payload.get("target_nodes", ["node-1", "node-2"])
    if not isinstance(target_nodes, list) or not target_nodes:
        raise ValueError("target_nodes must be a non-empty list")

    history_seed = [float(value) for value in payload.get("history_seed", [0.5, 0.6, 0.7])]
    if len(history_seed) < 3:
        raise ValueError("history_seed must contain at least 3 values")

    workload_mode = str(payload.get("workload_mode", "baseline"))
    if workload_mode not in {"baseline", "bursty-high-load", "mixed-low-load"}:
        raise ValueError("workload_mode must be one of 'baseline', 'bursty-high-load', or 'mixed-low-load'")

    workload_source = str(payload.get("workload_source", "service"))
    if workload_source not in {"service", "generated", "replay"}:
        raise ValueError("workload_source must be one of 'service', 'generated', or 'replay'")

    trace_seed = int(payload.get("trace_seed", 20260331))
    workload_trace_payload = payload.get("workload_trace")
    workload_trace_path_payload = payload.get("workload_trace_path")
    workload_trace: list[float] | None = None
    if workload_trace_payload is not None:
        if not isinstance(workload_trace_payload, list) or not workload_trace_payload:
            raise ValueError("workload_trace must be a non-empty list when provided")
        workload_trace = [max(0.0, min(1.0, float(value))) for value in workload_trace_payload]
    if workload_source == "replay":
        if workload_trace is None and workload_trace_path_payload is None:
            raise ValueError("workload_trace or workload_trace_path is required when workload_source is 'replay'")
        if workload_trace is None and workload_trace_path_payload is not None:
            workload_trace = _load_trace_file(path, workload_trace_path_payload)
        if len(workload_trace) < timesteps:
            raise ValueError("workload_trace must contain at least timesteps values for replay mode")

    policy = str(payload.get("policy", "proposed"))
    if policy not in {
        "proposed",
        "threshold",
        "reactive",
        "hpa-like",
        "predictive-only",
        "proposed-no-risk",
        "proposed-no-uncertainty",
        "proposed-no-agents",
    }:
        raise ValueError(
            "policy must be one of 'proposed', 'threshold', 'reactive', 'hpa-like', 'predictive-only', "
            "'proposed-no-risk', 'proposed-no-uncertainty', or 'proposed-no-agents'"
        )
    summary_metrics = payload.get(
        "summary_metrics",
        ["final_rmse", "average_utilization", "action_counts", "average_prediction", "average_risk"],
    )
    if not isinstance(summary_metrics, list) or not summary_metrics:
        raise ValueError("summary_metrics must be a non-empty list")

    risk_inputs_payload = payload.get("risk_inputs", {})
    if not isinstance(risk_inputs_payload, dict):
        raise ValueError("risk_inputs must be an object")

    cpu_source = str(risk_inputs_payload.get("cpu_source", "average"))
    memory_source = str(risk_inputs_payload.get("memory_source", "average"))
    uncertainty_source = str(risk_inputs_payload.get("uncertainty_source", "prediction"))

    for field_name, value in {"cpu_source": cpu_source, "memory_source": memory_source}.items():
        if value not in {"average", "max"}:
            raise ValueError(f"{field_name} must be either 'average' or 'max'")
    if uncertainty_source != "prediction":
        raise ValueError("uncertainty_source must currently be 'prediction'")

    service_urls = payload.get("service_urls")
    if service_urls is not None and (not isinstance(service_urls, dict) or not service_urls):
        raise ValueError("service_urls must be an object when provided")

    return ExperimentConfig(
        experiment_name=payload.get("experiment_name"),
        timesteps=timesteps,
        step_sleep_seconds=step_sleep_seconds,
        target_nodes=[str(node) for node in target_nodes],
        history_seed=history_seed,
        workload_mode=workload_mode,
        workload_source=workload_source,
        trace_seed=trace_seed,
        workload_trace=workload_trace,
        workload_trace_path=str(workload_trace_path_payload) if workload_trace_path_payload else None,
        policy=policy,
        risk_inputs=RiskInputStrategy(
            cpu_source=cpu_source,
            memory_source=memory_source,
            uncertainty_source=uncertainty_source,
        ),
        summary_metrics=[str(metric) for metric in summary_metrics],
        service_urls={**ExperimentConfig(experiment_name=None, timesteps=1).service_urls, **(service_urls or {})},
    )


def _load_trace_file(config_path: Path, raw_trace_path: Any) -> list[float]:
    trace_path = Path(str(raw_trace_path))
    if not trace_path.is_absolute():
        trace_path = (config_path.parent / trace_path).resolve()
    if not trace_path.exists():
        raise ValueError(f"workload_trace_path file not found: {trace_path}")

    if trace_path.suffix.lower() in {".yaml", ".yml"}:
        with trace_path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
        if isinstance(payload, dict):
            values = payload.get("trace")
        else:
            values = payload
        if not isinstance(values, list) or not values:
            raise ValueError("YAML trace files must contain a non-empty list or a 'trace' list key")
        return [max(0.0, min(1.0, float(value))) for value in values]

    if trace_path.suffix.lower() == ".json":
        import json

        with trace_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        values = payload.get("trace") if isinstance(payload, dict) else payload
        if not isinstance(values, list) or not values:
            raise ValueError("JSON trace files must contain a non-empty list or a 'trace' list key")
        return [max(0.0, min(1.0, float(value))) for value in values]

    if trace_path.suffix.lower() == ".csv":
        values: list[float] = []
        with trace_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames and "workload" in reader.fieldnames:
                for row in reader:
                    if row.get("workload") is not None and row["workload"] != "":
                        values.append(max(0.0, min(1.0, float(row["workload"]))))
            else:
                handle.seek(0)
                for raw_line in handle:
                    stripped = raw_line.strip()
                    if not stripped:
                        continue
                    values.append(max(0.0, min(1.0, float(stripped.split(",")[0]))))
        if not values:
            raise ValueError("CSV trace files must contain at least one workload value")
        return values

    raise ValueError("workload_trace_path must point to a .csv, .json, .yaml, or .yml file")

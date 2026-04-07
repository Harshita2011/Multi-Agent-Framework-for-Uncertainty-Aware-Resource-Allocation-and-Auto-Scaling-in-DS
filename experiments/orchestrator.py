"""Unified orchestration for research experiments."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import random
import re
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import yaml

from experiments.config_loader import ExperimentConfig


EXPERIMENT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
APP_SERVICES = [
    "node-service-1",
    "node-service-2",
    "workload-generator",
    "prediction-service",
    "risk-service",
    "agent-service",
    "resource-service",
    "allocation-service",
    "coordinator-service",
    "execution-service",
    "evaluation-service",
]


@dataclass(frozen=True)
class RunPaths:
    """Filesystem layout for a single experiment run."""

    root_dir: Path
    run_dir: Path
    config_path: Path
    csv_path: Path
    jsonl_path: Path
    summary_path: Path
    log_path: Path
    provenance_path: Path
    workload_trace_path: Path


class ExperimentError(RuntimeError):
    """Raised when the experiment cannot complete successfully."""


class ExperimentLogger:
    """Simple file-backed logger for experiment runs."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def log(self, message: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        line = f"[{timestamp}] {message}"
        print(line)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


class ExperimentRunLock:
    """Prevent overlapping experiment runs against the shared in-memory stack."""

    def __init__(self, lock_path: Path, experiment_name: str) -> None:
        self._lock_path = lock_path
        self._experiment_name = experiment_name

    def __enter__(self) -> "ExperimentRunLock":
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._lock_path.open("x", encoding="utf-8") as handle:
                handle.write(json.dumps({"experiment_name": self._experiment_name}))
        except FileExistsError as error:
            raise ExperimentError(
                "Another experiment run is already in progress. Wait for it to finish before starting a new run."
            ) from error
        return self

    def __exit__(self, exc_type: object, exc: object, exc_tb: object) -> None:
        if self._lock_path.exists():
            self._lock_path.unlink()


class ServiceClient:
    """HTTP client for the simulation services."""

    def __init__(self, service_urls: dict[str, str]) -> None:
        self._service_urls = service_urls
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    def close(self) -> None:
        self._session.close()

    def wait_until_ready(self, logger: ExperimentLogger, timeout_seconds: float = 90.0) -> None:
        """Poll FastAPI OpenAPI endpoints until the stack is responsive."""

        deadline = time.time() + timeout_seconds
        required_services = [
            "node-1",
            "node-2",
            "workload",
            "prediction",
            "risk",
            "agent",
            "resource",
            "allocation",
            "coordinator",
            "execution",
            "evaluation",
        ]

        while time.time() < deadline:
            failed_services: list[str] = []
            for service_name in required_services:
                url = f"{self._service_urls[service_name]}/openapi.json"
                try:
                    response = self._session.get(url, timeout=5)
                    response.raise_for_status()
                except requests.RequestException:
                    failed_services.append(service_name)

            if not failed_services:
                logger.log("All required services are reachable.")
                return

            logger.log(f"Waiting for services: {', '.join(failed_services)}")
            time.sleep(3)

        raise ExperimentError("Timed out waiting for Docker services to become ready")

    def get_node_metrics(self, node_name: str) -> dict[str, Any]:
        return self._get_json(f"{self._service_urls[node_name]}/metrics")

    def get_workload(self) -> dict[str, Any]:
        return self._get_json(f"{self._service_urls['workload']}/load")

    def predict(self, history: list[float]) -> dict[str, Any]:
        return self._post_json(f"{self._service_urls['prediction']}/predict", {"history": history})

    def compute_risk(self, cpu: float, memory: float, uncertainty: float) -> dict[str, Any]:
        return self._post_json(
            f"{self._service_urls['risk']}/risk",
            {"cpu": cpu, "memory": memory, "uncertainty": uncertainty},
        )

    def evaluate_agents(self, cpu: float, risk: float) -> dict[str, Any]:
        return self._post_json(f"{self._service_urls['agent']}/evaluate", {"cpu": cpu, "risk": risk})

    def get_resources(self) -> dict[str, Any]:
        return self._get_json(f"{self._service_urls['resource']}/resources")

    def allocate(self, cpu_required: float) -> dict[str, Any]:
        return self._post_json(
            f"{self._service_urls['allocation']}/allocate",
            {"cpu_required": cpu_required},
        )

    def decide(self, prediction: float, risk: float) -> dict[str, Any]:
        return self._post_json(
            f"{self._service_urls['coordinator']}/decide",
            {"prediction": prediction, "risk": risk},
        )

    def execute(self, action: str) -> dict[str, Any]:
        return self._post_json(f"{self._service_urls['execution']}/execute", {"action": action})

    def get_evaluation_metrics(self) -> dict[str, Any]:
        return self._get_json(f"{self._service_urls['evaluation']}/metrics")

    def record_observation(self, prediction: float, actual: float, utilization: float) -> dict[str, Any]:
        return self._post_json(
            f"{self._service_urls['evaluation']}/metrics/observations",
            {"prediction": prediction, "actual": actual, "utilization": utilization},
        )

    def _get_json(self, url: str) -> dict[str, Any]:
        try:
            response = self._session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as error:
            raise ExperimentError(f"GET {url} failed: {error}") from error
        if not isinstance(data, dict):
            raise ExperimentError(f"GET {url} returned a non-object payload")
        return data

    def _post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as error:
            raise ExperimentError(f"POST {url} failed: {error}") from error
        if not isinstance(data, dict):
            raise ExperimentError(f"POST {url} returned a non-object payload")
        return data


class WorkloadController:
    """Provides deterministic experiment workloads for stronger reproducibility."""

    def __init__(self, config: ExperimentConfig) -> None:
        self._config = config
        self._random = random.Random(config.trace_seed)
        self._generated_trace = self._build_generated_trace() if config.workload_source == "generated" else None

    def value_for_step(self, step_index: int, raw_service_workload: float | None) -> float:
        if self._config.workload_source == "replay":
            assert self._config.workload_trace is not None  # validated by config loader
            return round(self._config.workload_trace[step_index - 1], 2)
        if self._config.workload_source == "generated":
            assert self._generated_trace is not None
            return self._generated_trace[step_index - 1]
        if raw_service_workload is None:
            raise ExperimentError("A service workload is required when workload_source is 'service'")
        return _shape_workload(raw_service_workload, self._config.workload_mode, step_index)

    def trace_for_run(self, timesteps: int) -> list[float]:
        if self._config.workload_source == "replay":
            assert self._config.workload_trace is not None
            return [round(value, 2) for value in self._config.workload_trace[:timesteps]]
        if self._config.workload_source == "generated":
            assert self._generated_trace is not None
            return list(self._generated_trace[:timesteps])
        return []

    def _build_generated_trace(self) -> list[float]:
        baseline = sum(self._config.history_seed) / len(self._config.history_seed)
        phase = self._random.uniform(0.0, 6.283185307179586)
        trend = self._random.uniform(-0.015, 0.015)
        trace: list[float] = []
        for step_index in range(1, self._config.timesteps + 1):
            seasonal = 0.18 * math.sin(step_index / 2.5 + phase)
            secondary = 0.08 * math.cos(step_index / 4.0 + phase / 2.0)
            noise = self._random.uniform(-0.025, 0.025)
            raw_workload = _clamp(baseline + seasonal + secondary + (step_index - 1) * trend + noise)
            trace.append(_shape_workload(raw_workload, self._config.workload_mode, step_index))
        return trace


def collect_provenance(repo_root: Path, config: ExperimentConfig, config_path: Path) -> dict[str, Any]:
    """Capture lightweight provenance so runs are easier to audit later."""

    config_payload = config.to_dict()
    config_digest = hashlib.sha256(
        json.dumps(config_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    source_digest = hashlib.sha256(config_path.read_bytes()).hexdigest()

    git_commit = _run_capture(["git", "rev-parse", "HEAD"], repo_root)
    git_status = _run_capture(["git", "status", "--short"], repo_root)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config_source": str(config_path),
        "config_sha256": source_digest,
        "resolved_config_sha256": config_digest,
        "python_version": sys.version,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
        "git": {
            "commit": git_commit.strip() or None,
            "is_dirty": bool(git_status.strip()),
            "status_short": git_status.splitlines(),
        },
    }


def persist_provenance(path: Path, provenance: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(provenance, handle, indent=2)


def persist_workload_trace(path: Path, trace: list[float], source: str) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump({"workload_source": source, "trace": trace}, handle, indent=2)


def _run_capture(command: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def ensure_docker_is_available(repo_root: Path) -> None:
    """Validate Docker and the compose file before starting an experiment."""

    for command in (
        ["docker", "version"],
        ["docker", "compose", "config"],
    ):
        completed = subprocess.run(
            command,
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise ExperimentError(
                f"Command {' '.join(command)} failed.\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
            )

    running_services = subprocess.run(
        ["docker", "compose", "ps", "--services", "--status", "running"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if running_services.returncode != 0:
        raise ExperimentError(
            f"Command docker compose ps failed.\nSTDOUT:\n{running_services.stdout}\nSTDERR:\n{running_services.stderr}"
        )
    if "node-service-1" not in running_services.stdout:
        raise ExperimentError(
            "Docker Compose stack does not appear to be running. Start it with 'docker compose up --build -d' first."
        )


def reset_simulation_stack(repo_root: Path, logger: ExperimentLogger) -> None:
    """Restart the stateful app services for a clean experiment baseline."""

    logger.log("Resetting Docker app services to ensure a clean experiment state.")
    completed = subprocess.run(
        ["docker", "compose", "restart", *APP_SERVICES],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ExperimentError(
            f"Command docker compose restart failed.\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )


def validate_experiment_name(name: str) -> str:
    """Ensure experiment names are safe for directory creation."""

    if not EXPERIMENT_NAME_PATTERN.match(name):
        raise ExperimentError(
            "Experiment name must match the pattern [A-Za-z0-9][A-Za-z0-9._-]*"
        )
    return name


def prepare_run_paths(repo_root: Path, experiment_name: str) -> RunPaths:
    """Create the result directory structure for a single run."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root_dir = repo_root / "results" / experiment_name
    run_dir = root_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=False)
    return RunPaths(
        root_dir=root_dir,
        run_dir=run_dir,
        config_path=run_dir / "config.yaml",
        csv_path=run_dir / "step_logs.csv",
        jsonl_path=run_dir / "step_logs.jsonl",
        summary_path=run_dir / "summary.json",
        log_path=run_dir / "run.log",
        provenance_path=run_dir / "provenance.json",
        workload_trace_path=run_dir / "workload_trace.json",
    )


def persist_config(config: ExperimentConfig, source_path: Path, destination_path: Path) -> None:
    """Persist the resolved experiment config for reproducibility."""

    payload = config.to_dict()
    payload["config_source"] = str(source_path)
    with destination_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False)


def run_experiment(repo_root: Path, config: ExperimentConfig, config_path: Path, experiment_name: str) -> RunPaths:
    """Execute an experiment and persist a full research-grade bundle."""

    ensure_docker_is_available(repo_root)
    run_paths = prepare_run_paths(repo_root, experiment_name)
    logger = ExperimentLogger(run_paths.log_path)
    persist_config(config, config_path, run_paths.config_path)
    provenance = collect_provenance(repo_root, config, config_path)
    persist_provenance(run_paths.provenance_path, provenance)
    logger.log(f"Starting experiment '{experiment_name}' from {config_path}")

    summary: dict[str, Any] = {
        "experiment_name": experiment_name,
        "config_path": str(config_path),
        "run_timestamp": run_paths.run_dir.name,
        "policy": config.policy,
        "workload_mode": config.workload_mode,
        "workload_source": config.workload_source,
        "trace_seed": config.trace_seed,
        "total_timesteps_requested": config.timesteps,
        "total_timesteps_completed": 0,
        "final_rmse": None,
        "average_utilization": None,
        "action_counts": {},
        "average_prediction": None,
        "average_risk": None,
        "p95_utilization": None,
        "sla_violation_rate": None,
        "control_loop_latency_ms": None,
        "throughput_proxy": None,
        "cost_proxy": None,
        "action_churn_rate": None,
        "provenance_path": str(run_paths.provenance_path),
        "workload_trace_path": str(run_paths.workload_trace_path),
        "resolved_config_sha256": provenance["resolved_config_sha256"],
        "source_config_sha256": provenance["config_sha256"],
        "status": "running",
        "failure_reason": None,
    }
    _write_summary(run_paths.summary_path, summary)

    client = ServiceClient(config.service_urls)
    workload_controller = WorkloadController(config)
    persist_workload_trace(
        run_paths.workload_trace_path,
        workload_controller.trace_for_run(config.timesteps),
        config.workload_source,
    )
    history = list(config.history_seed)
    action_counter: Counter[str] = Counter()
    predictions: list[float] = []
    risks: list[float] = []
    utilizations: list[float] = []
    throughputs: list[float] = []
    costs: list[float] = []
    control_loop_latencies_ms: list[float] = []
    sla_violations = 0
    action_changes = 0
    previous_action: str | None = None
    step_rows: list[dict[str, Any]] = []
    csv_writer: csv.DictWriter[str] | None = None
    csv_file = run_paths.csv_path.open("w", newline="", encoding="utf-8")

    try:
        with ExperimentRunLock(repo_root / "results" / ".experiment.lock", experiment_name):
            reset_simulation_stack(repo_root, logger)
            client.wait_until_ready(logger)

            for step_index in range(1, config.timesteps + 1):
                step_start = time.perf_counter()
                step_timestamp = datetime.now(timezone.utc).isoformat()
                logger.log(f"Executing step {step_index}/{config.timesteps}")

                node_metrics = {}
                for node_name in config.target_nodes:
                    node_result, _ = _timed_call(lambda node_name=node_name: client.get_node_metrics(node_name))
                    node_metrics[node_name] = node_result

                service_workload, _ = _timed_call(client.get_workload)
                raw_service_workload = float(service_workload["load"])
                effective_workload = workload_controller.value_for_step(step_index, raw_service_workload)
                prediction, _ = _timed_call(lambda: client.predict(history))

                selected_cpu = _select_metric(node_metrics, "cpu", config.risk_inputs.cpu_source)
                selected_memory = _select_metric(node_metrics, "memory", config.risk_inputs.memory_source)
                effective_uncertainty = float(prediction["uncertainty"])
                if config.policy == "proposed-no-uncertainty":
                    effective_uncertainty = 0.0
                risk, _ = _timed_call(
                    lambda: client.compute_risk(selected_cpu, selected_memory, effective_uncertainty)
                )
                effective_risk = float(risk["risk_score"])
                if config.policy == "proposed-no-risk":
                    effective_risk = 0.0

                agent_scores, _ = _timed_call(lambda: client.evaluate_agents(selected_cpu, effective_risk))
                if config.policy == "proposed-no-agents":
                    agent_scores = {
                        "performance_score": 0.5,
                        "cost_score": 0.5,
                        "risk_score": 0.5,
                    }
                resources, _ = _timed_call(client.get_resources)
                allocation, _ = _timed_call(lambda: client.allocate(prediction["prediction"]))
                policy_decision = _decide_action(
                    policy=config.policy,
                    prediction=float(prediction["prediction"]),
                    risk=effective_risk,
                    selected_cpu=selected_cpu,
                    effective_workload=effective_workload,
                    previous_workload=history[-1],
                    performance_score=float(agent_scores["performance_score"]),
                    cost_score=float(agent_scores["cost_score"]),
                    agent_risk_score=float(agent_scores["risk_score"]),
                )
                coordinator_decision, _ = _timed_call(lambda: client.decide(prediction["prediction"], effective_risk))
                execution, _ = _timed_call(lambda: client.execute(policy_decision))
                evaluation, _ = _timed_call(
                    lambda: client.record_observation(
                    prediction=prediction["prediction"],
                    actual=effective_workload,
                    utilization=selected_cpu,
                )
                )

                step_latency_ms = round((time.perf_counter() - step_start) * 1000.0, 3)
                control_loop_latencies_ms.append(step_latency_ms)

                action_counter.update([policy_decision])
                if previous_action is not None and previous_action != policy_decision:
                    action_changes += 1
                previous_action = policy_decision
                predictions.append(prediction["prediction"])
                risks.append(effective_risk)
                utilizations.append(float(evaluation["utilization"]))
                if float(evaluation["utilization"]) >= 0.80:
                    sla_violations += 1
                throughputs.append(_throughput_proxy(effective_workload, float(evaluation["utilization"])))
                costs.append(_cost_proxy(policy_decision, float(evaluation["utilization"])))
                history.append(effective_workload)
                history = history[-max(len(config.history_seed), 3) :]

                row = {
                    "timestamp": step_timestamp,
                    "step_index": step_index,
                    "workload_mode": config.workload_mode,
                    "workload_source": config.workload_source,
                    "service_workload": raw_service_workload,
                    "workload": effective_workload,
                    "prediction": prediction["prediction"],
                    "uncertainty": prediction["uncertainty"],
                    "risk_score": effective_risk,
                    "policy": config.policy,
                    "performance_score": agent_scores["performance_score"],
                    "cost_score": agent_scores["cost_score"],
                    "agent_risk_score": agent_scores["risk_score"],
                    "resource_small": resources["small"],
                    "resource_medium": resources["medium"],
                    "resource_large": resources["large"],
                    "allocation_large": allocation["allocation"].get("large"),
                    "allocation_medium": allocation["allocation"].get("medium"),
                    "allocation_small": allocation["allocation"].get("small"),
                    "coordinator_action": coordinator_decision["action"],
                    "action": policy_decision,
                    "execution_status": execution["status"],
                    "rmse": evaluation["rmse"],
                    "utilization": evaluation["utilization"],
                    "control_loop_latency_ms": step_latency_ms,
                    "throughput_proxy": throughputs[-1],
                    "cost_proxy": costs[-1],
                    "sla_violation": 1 if float(evaluation["utilization"]) >= 0.80 else 0,
                }
                for node_name, metrics in node_metrics.items():
                    safe_node_name = node_name.replace("-", "_")
                    row[f"{safe_node_name}_cpu"] = metrics["cpu"]
                    row[f"{safe_node_name}_memory"] = metrics["memory"]
                    row[f"{safe_node_name}_timestamp"] = metrics["timestamp"]

                if csv_writer is None:
                    csv_writer = csv.DictWriter(csv_file, fieldnames=list(row.keys()))
                    csv_writer.writeheader()
                csv_writer.writerow(row)
                csv_file.flush()

                with run_paths.jsonl_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row) + "\n")

                step_rows.append(row)
                summary.update(
                    {
                        "total_timesteps_completed": step_index,
                        "final_rmse": evaluation["rmse"],
                        "average_utilization": round(sum(item["utilization"] for item in step_rows) / len(step_rows), 4),
                        "action_counts": dict(action_counter),
                        "average_prediction": round(sum(predictions) / len(predictions), 4),
                        "average_risk": round(sum(risks) / len(risks), 4),
                        "p95_utilization": round(_percentile(utilizations, 0.95), 4),
                        "sla_violation_rate": round(sla_violations / len(step_rows), 4),
                        "control_loop_latency_ms": round(sum(control_loop_latencies_ms) / len(control_loop_latencies_ms), 4),
                        "throughput_proxy": round(sum(throughputs) / len(throughputs), 4),
                        "cost_proxy": round(sum(costs) / len(costs), 4),
                        "action_churn_rate": round(action_changes / max(1, len(step_rows) - 1), 4),
                        "status": "running",
                        "failure_reason": None,
                    }
                )
                _write_summary(run_paths.summary_path, summary)

                if config.step_sleep_seconds > 0:
                    time.sleep(config.step_sleep_seconds)

        summary["status"] = "success"
        _write_summary(run_paths.summary_path, summary)
        logger.log(f"Experiment '{experiment_name}' completed successfully.")
        return run_paths

    except Exception as error:
        summary["status"] = "failed"
        summary["failure_reason"] = str(error)
        _write_summary(run_paths.summary_path, summary)
        logger.log(f"Experiment failed: {error}")
        raise

    finally:
        csv_file.close()
        client.close()


def _select_metric(node_metrics: dict[str, dict[str, Any]], key: str, strategy: str) -> float:
    values = [float(metrics[key]) for metrics in node_metrics.values()]
    if strategy == "max":
        return max(values)
    return sum(values) / len(values)


def _decide_action(
    policy: str,
    prediction: float,
    risk: float,
    selected_cpu: float,
    effective_workload: float,
    previous_workload: float,
    performance_score: float,
    cost_score: float,
    agent_risk_score: float,
) -> str:
    if policy == "threshold":
        if selected_cpu >= 0.72 or effective_workload >= 0.78:
            return "scale_up"
        if selected_cpu <= 0.38 and effective_workload <= 0.35:
            return "scale_down"
        return "hold"

    if policy == "reactive":
        delta = effective_workload - previous_workload
        if delta >= 0.12 or selected_cpu >= 0.75:
            return "scale_up"
        if delta <= -0.12 and selected_cpu <= 0.45:
            return "scale_down"
        return "hold"

    if policy == "hpa-like":
        if selected_cpu >= 0.70:
            return "scale_up"
        if selected_cpu <= 0.35:
            return "scale_down"
        return "hold"

    if policy == "predictive-only":
        if prediction >= 0.62:
            return "scale_up"
        if prediction <= 0.34:
            return "scale_down"
        return "hold"

    # Proposed family: blend uncertainty-aware risk with agent utility signals.
    pressure = (0.5 * prediction) + (0.3 * risk) + (0.2 * performance_score)
    release = (0.5 * (1.0 - prediction)) + (0.3 * (1.0 - risk)) + (0.2 * cost_score)
    risk_guard = max(risk, agent_risk_score)

    if pressure >= 0.58 and risk_guard >= 0.38:
        return "scale_up"
    if release >= 0.60 and risk <= 0.42 and selected_cpu <= 0.45:
        return "scale_down"
    return "hold"


def _shape_workload(raw_workload: float, workload_mode: str, step_index: int) -> float:
    """Turn the generic workload signal into a reproducible scenario profile."""

    if workload_mode == "bursty-high-load":
        burst = 0.22 if step_index % 2 == 1 else 0.12
        return round(_clamp(raw_workload * 1.15 + burst), 2)
    if workload_mode == "mixed-low-load":
        reduction = 0.18 if step_index % 2 == 1 else 0.10
        return round(_clamp(raw_workload * 0.70 - reduction), 2)
    return round(_clamp(raw_workload), 2)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _write_summary(path: Path, summary: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)


def _timed_call(func: Any) -> tuple[Any, float]:
    start = time.perf_counter()
    result = func()
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return result, elapsed_ms


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    fraction = position - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * fraction


def _throughput_proxy(workload: float, utilization: float) -> float:
    return round(1000.0 * workload * (1.0 - max(0.0, utilization - 0.85)), 4)


def _cost_proxy(action: str, utilization: float) -> float:
    action_penalty = {"scale_up": 0.12, "hold": 0.08, "scale_down": 0.05}.get(action, 0.08)
    return round(utilization + action_penalty, 4)

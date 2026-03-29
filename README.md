# Multi-Agent Framework for Uncertainty-Aware Resource Allocation and Auto-Scaling in DS

This repository is being built phase by phase.

Phase 1 delivers two FastAPI microservices:

- `node-service`: simulates per-node CPU and memory metrics
- `workload-generator`: produces a changing load signal

Phase 2 adds monitoring for `node-service` with Prometheus-compatible metrics and a starter Grafana dashboard.

## Current Structure

```text
services/
|-- node-service/
|   \-- app/
|       |-- __init__.py
|       |-- main.py
|       |-- metrics.py
|       |-- routes.py
|       \-- simulator.py
|-- workload-generator/
|   \-- app/
|       |-- __init__.py
|       |-- generator.py
|       \-- main.py
\-- infra/
    |-- grafana/
    |   \-- dashboards/
    |       \-- node-service-dashboard.json
    \-- prometheus/
        \-- prometheus.yml
```

## Requirements

- Python 3.11+
- `pip`

Install dependencies:

```powershell
pip install fastapi uvicorn prometheus-client
```

## Run Services

Open separate terminals from the repository root.

Start `node-service` as `node-1`:

```powershell
cd services\node-service
$env:NODE_ID="node-1"
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Start `node-service` as `node-2`:

```powershell
cd services\node-service
$env:NODE_ID="node-2"
uvicorn app.main:app --host 127.0.0.1 --port 8002
```

Start `workload-generator`:

```powershell
cd services\workload-generator
uvicorn app.main:app --host 127.0.0.1 --port 8003
```

## API Endpoints

Node metrics JSON:

```text
GET /metrics
```

Example response:

```json
{
  "node_id": "node-1",
  "cpu": 0.65,
  "memory": 0.72,
  "timestamp": 1710000000
}
```

Prometheus scrape endpoint:

```text
GET /metrics/prometheus
```

Example response:

```text
cpu_usage{node_id="node-1"} 0.65
memory_usage{node_id="node-1"} 0.72
```

Workload load:

```text
GET /load
```

Example response:

```json
{
  "load": 0.7
}
```

## Verify Phase 1

Check both nodes:

```powershell
Invoke-RestMethod http://127.0.0.1:8001/metrics
Invoke-RestMethod http://127.0.0.1:8002/metrics
```

Check workload generator:

```powershell
Invoke-RestMethod http://127.0.0.1:8003/load
```

Check that values change over time:

```powershell
1..5 | ForEach-Object { Invoke-RestMethod http://127.0.0.1:8001/metrics; Start-Sleep 2 }
1..5 | ForEach-Object { Invoke-RestMethod http://127.0.0.1:8002/metrics; Start-Sleep 2 }
1..5 | ForEach-Object { Invoke-RestMethod http://127.0.0.1:8003/load; Start-Sleep 2 }
```

## Verify Phase 2

Check the Prometheus scrape output:

```powershell
Invoke-WebRequest http://127.0.0.1:8001/metrics/prometheus | Select-Object -ExpandProperty Content
Invoke-WebRequest http://127.0.0.1:8002/metrics/prometheus | Select-Object -ExpandProperty Content
```

Phase 1 is considered valid when:

- both node services respond independently
- CPU and memory values change over time
- workload values change over time
- API responses match the phase contract

Phase 2 is considered valid when:

- Prometheus successfully scrapes `/metrics/prometheus`
- `cpu_usage` and `memory_usage` appear in Prometheus
- the Grafana dashboard shows both metrics in real time

## Prometheus Setup

The Prometheus configuration is stored at `infra/prometheus/prometheus.yml`.

It is configured to scrape:

- `host.docker.internal:8001`
- `host.docker.internal:8002`

If you run Prometheus directly on Windows instead of Docker, replace those targets with:

- `127.0.0.1:8001`
- `127.0.0.1:8002`

## Grafana Setup

A starter dashboard is available at `infra/grafana/dashboards/node-service-dashboard.json`.

Import it into Grafana after adding a Prometheus data source with UID `prometheus`.

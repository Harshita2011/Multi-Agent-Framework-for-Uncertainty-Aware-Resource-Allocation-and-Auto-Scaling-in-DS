# Multi-Agent Framework for Uncertainty-Aware Resource Allocation and Auto-Scaling in DS

This repository is being built phase by phase.

Phase 1 delivers two FastAPI microservices:

- `node-service`: simulates per-node CPU and memory metrics
- `workload-generator`: produces a changing load signal

Phase 2 adds monitoring for `node-service` with Prometheus-compatible metrics and a starter Grafana dashboard.

Phase 3 adds `prediction-service`, a lightweight recurrent forecasting API that returns both a prediction and an uncertainty score.

Phase 4 adds `risk-service`, which computes an interpretable instability score from utilization and prediction uncertainty.

Phase 5 adds `agent-service`, which evaluates a node through simple performance, cost, and risk agents.

Phase 6 adds `resource-service`, which tracks the in-memory node pool and availability by node type.

Phase 7 adds `allocation-service`, which computes greedy node selections for requested CPU capacity.

Phase 8 adds `coordinator-service`, which combines prediction and risk into a central scaling decision.

Phase 9 adds `execution-service`, which simulates applying actions such as scaling and isolation.

Phase 10 adds `evaluation-service`, which computes RMSE and utilization metrics from in-memory observations.

Phase 11 adds Docker support for every service plus a `docker-compose.yml` that brings the stack up together with Prometheus and Grafana.

Phase 12 adds Kubernetes manifests under `infra/k8s/` for the application services, Prometheus, and Grafana.

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
|-- agent-service/
|   \-- app/
|       |-- __init__.py
|       |-- agents.py
|       |-- main.py
|       \-- routes.py
|-- allocation-service/
|   \-- app/
|       |-- __init__.py
|       |-- main.py
|       |-- planner.py
|       \-- routes.py
|-- coordinator-service/
|   \-- app/
|       |-- __init__.py
|       |-- engine.py
|       |-- main.py
|       \-- routes.py
|-- evaluation-service/
|   \-- app/
|       |-- __init__.py
|       |-- engine.py
|       |-- main.py
|       \-- routes.py
|-- execution-service/
|   \-- app/
|       |-- __init__.py
|       |-- executor.py
|       |-- main.py
|       \-- routes.py
|-- infra/
|   |-- grafana/
|   |   |-- dashboards/
|   |   |   \-- node-service-dashboard.json
|   |   \-- provisioning/
|   |       |-- dashboards/
|   |       |   \-- dashboard.yml
|   |       \-- datasources/
|   |           \-- prometheus.yml
|   |-- k8s/
|   |   |-- application-services.yaml
|   |   |-- namespace.yaml
|   |   \-- observability.yaml
|   \-- prometheus/
|       \-- prometheus.yml
|-- prediction-service/
|   \-- app/
|       |-- __init__.py
|       |-- inference.py
|       |-- main.py
|       |-- model.py
|       \-- routes.py
|-- resource-service/
|   \-- app/
|       |-- __init__.py
|       |-- main.py
|       |-- manager.py
|       \-- routes.py
|-- risk-service/
|   \-- app/
|       |-- __init__.py
|       |-- engine.py
|       |-- main.py
|       \-- routes.py
|-- workload-generator/
|   \-- app/
|       |-- __init__.py
|       |-- generator.py
|       \-- main.py
|-- requirements.txt
\-- docker-compose.yml
```

## Requirements

- Python 3.11+
- `pip`

Install dependencies:

```powershell
pip install fastapi uvicorn prometheus-client
```

Docker files added in Phase 11:

- one `Dockerfile` inside each service directory
- root [docker-compose.yml](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/docker-compose.yml)
- root [requirements.txt](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/requirements.txt)

## Run Services

Open separate terminals from the repository root.

Start `node-service` as `node-1`:

```powershell
cd services\node-service
$env:NODE_ID="node-1"
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Start `agent-service`:

```powershell
cd services\agent-service
uvicorn app.main:app --host 127.0.0.1 --port 8006
```

Start `allocation-service`:

```powershell
cd services\allocation-service
uvicorn app.main:app --host 127.0.0.1 --port 8008
```

Start `coordinator-service`:

```powershell
cd services\coordinator-service
uvicorn app.main:app --host 127.0.0.1 --port 8009
```

Start `execution-service`:

```powershell
cd services\execution-service
uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Start `evaluation-service`:

```powershell
cd services\evaluation-service
uvicorn app.main:app --host 127.0.0.1 --port 8011
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

Start `prediction-service`:

```powershell
cd services\prediction-service
uvicorn app.main:app --host 127.0.0.1 --port 8004
```

Start `resource-service`:

```powershell
cd services\resource-service
uvicorn app.main:app --host 127.0.0.1 --port 8007
```

Start `risk-service`:

```powershell
cd services\risk-service
uvicorn app.main:app --host 127.0.0.1 --port 8005
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

Prediction endpoint:

```text
POST /predict
```

Example request:

```json
{
  "history": [0.5, 0.6, 0.7]
}
```

Example response:

```json
{
  "prediction": 0.79,
  "uncertainty": 0.1
}
```

Risk endpoint:

```text
POST /risk
```

Example request:

```json
{
  "cpu": 0.8,
  "memory": 0.7,
  "uncertainty": 0.1
}
```

Example response:

```json
{
  "risk_score": 0.53
}
```

Agent evaluation endpoint:

```text
POST /evaluate
```

Example request:

```json
{
  "cpu": 0.8,
  "risk": 0.7
}
```

Example response:

```json
{
  "performance_score": 0.79,
  "cost_score": 0.23,
  "risk_score": 0.7
}
```

Resource pool endpoint:

```text
GET /resources
```

Example response:

```json
{
  "small": 5,
  "medium": 3,
  "large": 2
}
```

Allocation endpoint:

```text
POST /allocate
```

Example request:

```json
{
  "cpu_required": 1.0
}
```

Example response:

```json
{
  "allocation": {
    "medium": 2
  }
}
```

Coordinator endpoint:

```text
POST /decide
```

Example request:

```json
{
  "prediction": 0.8,
  "risk": 0.6
}
```

Example response:

```json
{
  "action": "scale_up"
}
```

Execution endpoint:

```text
POST /execute
```

Example request:

```json
{
  "action": "scale_up"
}
```

Example response:

```json
{
  "status": "success"
}
```

Evaluation metrics endpoint:

```text
GET /metrics
```

Example response:

```json
{
  "rmse": 0.05,
  "utilization": 0.78
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
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8001/metrics/prometheus | Select-Object -ExpandProperty Content
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8002/metrics/prometheus | Select-Object -ExpandProperty Content
```

## Verify Phase 3

Start `prediction-service`, then test an increasing and decreasing history:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8004/predict -ContentType "application/json" -Body '{"history":[0.5,0.6,0.7]}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8004/predict -ContentType "application/json" -Body '{"history":[0.7,0.55,0.45,0.4]}'
```

## Verify Phase 4

Start `risk-service`, then compare low-load and high-load inputs:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8005/risk -ContentType "application/json" -Body '{"cpu":0.3,"memory":0.35,"uncertainty":0.05}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8005/risk -ContentType "application/json" -Body '{"cpu":0.8,"memory":0.7,"uncertainty":0.1}'
```

## Verify Phase 5

Start `agent-service`, then evaluate lower-risk and higher-risk inputs:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8006/evaluate -ContentType "application/json" -Body '{"cpu":0.4,"risk":0.2}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8006/evaluate -ContentType "application/json" -Body '{"cpu":0.8,"risk":0.7}'
```

## Verify Phase 6

Start `resource-service`, inspect the pool, then allocate and release one node:

```powershell
Invoke-RestMethod http://127.0.0.1:8007/resources
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8007/resources/allocate -ContentType "application/json" -Body '{"node_type":"small","count":1}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8007/resources/release -ContentType "application/json" -Body '{"node_type":"small","count":1}'
```

## Verify Phase 7

Start `allocation-service`, then test a few CPU requirements:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8008/allocate -ContentType "application/json" -Body '{"cpu_required":1.0}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8008/allocate -ContentType "application/json" -Body '{"cpu_required":2.25}'
```

## Verify Phase 8

Start `coordinator-service`, then test high-pressure and low-pressure inputs:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8009/decide -ContentType "application/json" -Body '{"prediction":0.8,"risk":0.6}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8009/decide -ContentType "application/json" -Body '{"prediction":0.3,"risk":0.2}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8009/decide -ContentType "application/json" -Body '{"prediction":0.55,"risk":0.45}'
```

## Verify Phase 9

Start `execution-service`, then execute a couple of actions and inspect the history:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8010/execute -ContentType "application/json" -Body '{"action":"scale_up"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8010/execute -ContentType "application/json" -Body '{"action":"isolate"}'
Invoke-RestMethod http://127.0.0.1:8010/execution/history
```

## Verify Phase 10

Start `evaluation-service`, inspect the current metrics, then add one observation:

```powershell
Invoke-RestMethod http://127.0.0.1:8011/metrics
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8011/metrics/observations -ContentType "application/json" -Body '{"prediction":0.82,"actual":0.78,"utilization":0.83}'
Invoke-RestMethod http://127.0.0.1:8011/metrics
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

Phase 3 is considered valid when:

- `prediction-service` responds on `/predict`
- increasing histories produce higher next-step predictions
- uncertainty increases as input variation increases

Phase 4 is considered valid when:

- `risk-service` responds on `/risk`
- higher load produces a higher `risk_score`
- the score stays interpretable and normalized

Phase 5 is considered valid when:

- `agent-service` responds on `/evaluate`
- `performance_score`, `cost_score`, and `risk_score` reflect the input values
- the output remains structured and normalized

Phase 6 is considered valid when:

- `resource-service` responds on `/resources`
- node counts are tracked in memory by type
- allocate and release requests update the counts correctly

Phase 7 is considered valid when:

- `allocation-service` responds on `/allocate`
- larger fitting node types are preferred first
- the selected node combination covers the requested CPU requirement

Phase 8 is considered valid when:

- `coordinator-service` responds on `/decide`
- high prediction and risk lead to `scale_up`
- low prediction and risk lead to `scale_down`
- intermediate cases return `hold`

Phase 9 is considered valid when:

- `execution-service` responds on `/execute`
- supported actions return `status: success`
- executed actions are reflected in the in-memory history

Phase 10 is considered valid when:

- `evaluation-service` responds on `/metrics`
- RMSE is computed from prediction vs actual samples
- utilization reflects the tracked average utilization

Phase 11 is considered valid when:

- each service has a working Dockerfile
- `docker-compose.yml` brings the services up together
- Prometheus scrapes the containerized node services
- Grafana starts with the provisioned Prometheus data source and dashboard

Phase 12 is considered valid when:

- Kubernetes namespace, Deployment, and Service manifests exist
- app services and observability components have clean manifests
- pods can be created successfully from the manifests

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

## Docker Compose

Build and start the full stack:

```powershell
docker compose up --build
```

Key ports:

- `8001` and `8002`: node services
- `8003` to `8011`: remaining application services
- `9090`: Prometheus
- `3000`: Grafana

Stop the stack:

```powershell
docker compose down
```

## Kubernetes

Apply the namespace and manifests:

```powershell
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/application-services.yaml
kubectl apply -f infra/k8s/observability.yaml
```

Check pod status:

```powershell
kubectl get pods -n ds-system
kubectl get services -n ds-system
```

Note:
- the manifests use local image names such as `node-service:latest`
- build and load those images into your cluster before applying the manifests if your cluster does not share the local Docker daemon

# Phase 2: Monitoring Integration

## Objective

Integrate Prometheus and expose metrics.

---

## Scope

* node-service
* Prometheus setup

---

## Tasks

* Add Prometheus client to node-service
* Expose /metrics endpoint
* Configure Prometheus scraping
* Setup basic Grafana dashboard

---

## Folder Changes

infra/
├── prometheus/
│   └── prometheus.yml

services/node-service/
├── metrics.py

---

## API Contracts

### Node Service

#### GET /metrics (Prometheus format)

Response:
Prometheus metrics format (text-based)

Example:

```
cpu_usage 0.65
memory_usage 0.72
```

---

## Validation Criteria

* Prometheus scrapes node metrics
* Metrics visible in Prometheus UI
* Grafana dashboard shows CPU/memory

---

## Constraints

* No business logic changes
* Only observability added

---

## Expected Output

* Metrics visible in Grafana
* Real-time updates

---

## Codex Prompt

You are implementing Phase 2: monitoring integration.

Requirements:

* Integrate Prometheus client in FastAPI node service
* Expose metrics in Prometheus format
* Add clear metric naming (cpu_usage, memory_usage)
* Provide Prometheus config file

Guidelines:

* Do not break existing APIs
* Keep monitoring separate from business logic
* Add comments explaining metrics

Ensure:

* Metrics are scrapeable
* Code is clean and modular

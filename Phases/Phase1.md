# Phase 1: Core Simulation Engine

## Objective

Build workload generator and node simulation with FastAPI.

---

## Scope

* workload-generator
* node-service

---

## Tasks

* Create FastAPI service for node
* Simulate CPU & memory usage
* Create workload generator
* Expose metrics via API

---

## Folder Changes

services/
├── node-service/
│   ├── main.py
│   ├── simulator.py
│   └── routes.py
│
├── workload-generator/
│   ├── main.py
│   └── generator.py

---

## API Contracts

### Node Service

#### GET /metrics

Response:

```json
{
  "node_id": "node-1",
  "cpu": 0.65,
  "memory": 0.72,
  "timestamp": 1710000000
}
```

---

### Workload Generator

#### GET /load

Response:

```json
{
  "load": 0.7
}
```

---

## Validation Criteria

* Multiple nodes simulate independently
* CPU/memory values change over time
* Workload generator produces dynamic load

---

## Constraints

* No ML yet
* No persistence
* Keep simulation simple

---

## Expected Output

* Running FastAPI services
* Metrics accessible via API

---

## Codex Prompt

You are implementing Phase 1 of a distributed simulation system.

Requirements:

* Use FastAPI
* Create two services: node-service and workload-generator
* Node service simulates CPU and memory dynamically
* Workload generator returns dynamic load patterns
* Keep code modular and clean
* Use type hints and docstrings
* Add comments explaining logic

Do NOT add unnecessary complexity.

Ensure:

* Code is runnable
* APIs match the contract exactly
* Simulation is realistic but simple

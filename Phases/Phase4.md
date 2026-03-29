# Phase 4: Risk & Stability Engine

## Objective

Compute instability score.

## Scope

* risk-service

## Tasks

* Compute variance
* Combine with utilization + uncertainty

## API Contracts

### POST /risk

```json
{
  "cpu": 0.8,
  "memory": 0.7,
  "uncertainty": 0.1
}
```

Response:

```json
{
  "risk_score": 0.75
}
```

## Validation

* High load → high risk

## Codex Prompt

Implement risk scoring logic using simple formula.
Keep it interpretable and modular.

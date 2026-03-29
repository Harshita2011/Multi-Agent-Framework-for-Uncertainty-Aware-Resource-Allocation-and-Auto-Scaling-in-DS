# Phase 5: Multi-Agent System

## Objective

Evaluate nodes via agents.

## Scope

* agent-service

## Tasks

* Performance agent
* Cost agent
* Risk agent

## API

### POST /evaluate

```json
{
  "cpu": 0.8,
  "risk": 0.7
}
```

Response:

```json
{
  "performance_score": 0.9,
  "cost_score": 0.4,
  "risk_score": 0.7
}
```

## Validation

* Scores reflect input

## Codex Prompt

Implement 3 agents as functions.
Return structured scores.
Keep logic simple and explainable.

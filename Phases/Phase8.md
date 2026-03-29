# Phase 8: Coordinator

## Objective

Central decision engine.

## Tasks

* Combine all inputs
* Decide action

## API

### POST /decide

```json
{
  "prediction": 0.8,
  "risk": 0.6
}
```

Response:

```json
{
  "action": "scale_up"
}
```

## Validation

* Logical decisions

## Codex Prompt

Combine scores and prediction.
Return action.
Keep logic modular.

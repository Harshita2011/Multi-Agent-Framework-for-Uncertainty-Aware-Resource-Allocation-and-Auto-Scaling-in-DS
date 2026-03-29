# Phase 7: Greedy Allocation

## Objective

Allocate resources.

## Tasks

* Implement greedy selection

## API

### POST /allocate

```json
{
  "cpu_required": 1.0
}
```

Response:

```json
{
  "allocation": {
    "medium": 2
  }
}
```

## Validation

* Correct combinations selected

## Codex Prompt

Implement greedy allocation logic.
Prefer larger nodes first.
Keep logic readable.

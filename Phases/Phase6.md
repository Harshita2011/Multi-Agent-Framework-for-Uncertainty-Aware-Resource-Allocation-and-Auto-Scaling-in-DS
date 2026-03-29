# Phase 6: Resource Manager

## Objective

Manage node pool.

## Tasks

* Define node types
* Track availability

## API

### GET /resources

```json
{
  "small": 5,
  "medium": 3,
  "large": 2
}
```

## Validation

* Resource counts update correctly

## Codex Prompt

Implement resource tracking service.
Keep state in memory.
Ensure clean structure.

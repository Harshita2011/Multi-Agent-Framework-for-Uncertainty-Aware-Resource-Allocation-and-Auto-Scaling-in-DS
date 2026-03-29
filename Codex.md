# CODEX.md

## Purpose

Guide the coding agent to build a modular, production-grade distributed system step-by-step using phase files.

---

## Core Principles

* Follow phase-by-phase implementation strictly
* Do NOT jump ahead
* Each phase must be complete and validated before moving on
* Code must be clean, modular, and testable

---

## Engineering Standards

* Use FastAPI for all services
* Use Python with type hints
* Follow PEP8
* Add meaningful comments (educational, not redundant)
* Use clear function and variable names
* Avoid hardcoding values

---

## Architecture Rules

* Microservices-based design
* Each service is independent
* Communication via REST APIs
* Shared schemas must be consistent
* Keep services loosely coupled

---

## Code Quality

* Functions must be small and focused
* Avoid duplication
* Use helper modules where needed
* Log important events

---

## Observability

* Every service should expose metrics when required
* Use Prometheus-compatible format
* Logs should be structured

---

## Development Workflow

For each phase:

1. Read phase file
2. Implement only listed tasks
3. Match API contracts exactly
4. Validate before proceeding

---

## Behavior Guidelines

* Prefer simple solutions over complex ones
* Do not introduce unnecessary frameworks
* Do not optimize prematurely
* Keep system extensible

---

## Output Expectations

* Runnable services
* Clear structure
* Consistent APIs
* Easy to extend to Kubernetes

---

## Important

If something is unclear:

* Follow API contract strictly
* Keep implementation minimal and correct

Do NOT:

* Add extra features
* Skip validation
* Break previous phases

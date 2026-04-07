# Project Presentation Summary

## Project Title

Multi-Agent Framework for Uncertainty-Aware Resource Allocation and Auto-Scaling in Distributed Systems

## What This Project Does

This project simulates how a distributed system can make smarter scaling decisions by combining:

- workload prediction
- uncertainty estimation
- risk scoring
- multi-agent evaluation
- resource allocation
- centralized coordination

Instead of only reacting to fixed thresholds, the system tries to make more informed scaling decisions under changing conditions.

## Core Idea

The main idea is simple:

1. simulate node metrics and workload
2. predict future demand
3. estimate uncertainty and risk
4. evaluate the system from multiple viewpoints
5. decide whether to scale up, scale down, or hold
6. log and compare the results across repeated experiments

## Main Components

- `node-service`: simulates node CPU and memory
- `workload-generator`: produces changing load
- `prediction-service`: predicts next-step demand
- `risk-service`: calculates risk from utilization and uncertainty
- `agent-service`: gives performance, cost, and risk assessments
- `resource-service`: tracks available resources
- `allocation-service`: selects resources greedily
- `coordinator-service`: original decision logic
- `execution-service`: simulates actions
- `evaluation-service`: tracks RMSE and utilization
- `experiments`: runs repeatable research experiments

## Technologies Used

- Python
- FastAPI
- Docker Compose
- Kubernetes manifests
- Prometheus
- Grafana

## What Makes It Strong

- modular microservice architecture
- Docker-first reproducibility
- Prometheus and Grafana monitoring
- persistent experiment logging
- repeated batch experiments
- confidence intervals in the final results
- paper-ready Markdown and LaTeX outputs

## Policies Compared

The project compares three decision policies:

- `proposed`
  Uses prediction and uncertainty-aware risk information.

- `threshold`
  Uses simple threshold rules.

- `reactive`
  Uses short-term workload changes.

## Final Validated Experiment

The strongest experiment completed in this project was:

- 30 total runs
- 10 runs per policy
- 20 timesteps per run
- 100% successful execution

Main result folder:

- [results/policy-compare-10b/20260329T173343Z](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/results/policy-compare-10b/20260329T173343Z)

## Key Findings

- The proposed policy showed more adaptive behavior than the baseline policies.
- The threshold and reactive baselines stayed almost entirely in `hold`.
- The proposed policy produced both `scale_up` and `scale_down` actions.
- The proposed policy achieved the lowest mean risk in the final policy-comparison batch.
- The framework now supports repeated experiments, confidence intervals, and generated plots.

## Why This Matters

This project goes beyond a simple demo because it does not only show that services run. It also shows:

- how the architecture behaves under repeated experiments
- how different policies compare
- how results can be logged and reported in a reproducible way

## Current Research Level

This project is best described as:

- a strong research prototype
- stronger than a basic course demo
- not yet a full production system

## Best Supporting Files

- [README.md](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/README.md)
- [PROJECT.md](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/PROJECT.md)
- [RESULTS.md](d:/DS1/Multi-Agent-Framework-for-Uncertainty-Aware-Resource-Allocation-and-Auto-Scaling-in-DS/RESULTS.md)

## Short Closing Statement

This project demonstrates a reproducible uncertainty-aware auto-scaling framework with multi-agent reasoning, monitoring, baseline-policy comparison, and batch experiment reporting. It provides a solid foundation for academic submission, project presentation, and future research extension.

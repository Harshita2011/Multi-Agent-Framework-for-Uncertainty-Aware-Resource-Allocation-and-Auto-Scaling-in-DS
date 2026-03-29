# Phase 3: Prediction Service

## Objective

Implement time-series prediction with uncertainty.

## Scope

* prediction-service

## Tasks

* Build LSTM/GRU model
* Create prediction API
* Output prediction + uncertainty

## Folder Changes

services/prediction-service/
├── main.py
├── model.py
├── inference.py

## API Contracts

### POST /predict

Request:

```json
{
  "history": [0.5, 0.6, 0.7]
}
```

Response:

```json
{
  "prediction": 0.75,
  "uncertainty": 0.08
}
```

## Validation Criteria

* Predictions follow trend
* Uncertainty reflects variation

## Constraints

* Keep model lightweight

## Expected Output

* Working prediction API

## Codex Prompt

Implement prediction-service using FastAPI.
Use simple LSTM/GRU.
Return prediction + uncertainty.
Keep code clean, modular, and well-commented.

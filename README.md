# License Plate Detection and Output Validation System

## Overview

This repository scaffolds a Python-based license plate detection and payload validation system focused on the detection and capture phase rather than full optical character recognition (OCR).

The solution includes:

- OpenCV-based region detection for license plate-like visual text arrays
- Structured JSON payload generation and validation
- Execution-level logging, error-tracking, and edge-case flagging
- Mock distributed processing using FastAPI endpoints simulating 5+ nodes
- Test scaffolding and validation guidance for strict QA

## Architecture

1. `app/detector.py` - Detects rectangular license plate regions from simulated image streams.
2. `app/payload.py` - Wraps capture data into rich JSON payloads with metadata and validation state.
3. `app/router.py` - Simulates request routing across distributed nodes and tracks load.
4. `app/node_api.py` - FastAPI node endpoint that accepts payloads and returns validation responses.
5. `app/execution.py` - Orchestrates stream simulation, capture, routing, and logging.
6. `app/logger.py` - Centralized logging and metrics for error rates and edge-case captures.

## Getting Started

### Requirements

- Python 3.12+
- `pip install -r requirements.txt`

### Run locally

1. Build and run one node:
   ```bash
   python main.py
   ```
2. Start the full distributed mock system:
   ```bash
   docker compose up --build
   ```

## Endpoints

Each node exposes a POST endpoint at `/process`.
Example payload structure:

```json
{
  "request_id": "...",
  "node_id": "node1",
  "timestamp": "...",
  "capture": {
    "region_id": "...",
    "confidence": 0.87,
    "bounds": { "x": 10, "y": 20, "width": 140, "height": 40 },
    "image_summary": "simulated-stream-0001"
  },
  "validation": {
    "status": "captured",
    "issues": []
  }
}
```

## Testing

Run tests with:

```bash
pytest -q
```

## Validation Protocol

- Every capture is validated for region confidence and bounding box size.
- Edge-case failures are logged when captures are missing, too-small, or ambiguous.
- Error rates are aggregated across payloads and surfaced periodically.
- The system is built to support simulated daily load of 50,000+ requests by using asynchronous endpoint processing and routing.

## Notes

This scaffold emphasizes detection and payload validation. A full OCR stage is intentionally omitted so the system can focus on robust capture, routing, and quality monitoring.

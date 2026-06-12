import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from app.payload import load_payload, LicensePlatePayload
from app.logger import configure_logger, MetricsTracker

app = FastAPI(title="License Plate Processing Node")
logger = configure_logger()
metrics = MetricsTracker()
NODE_ID = os.getenv("NODE_ID", "local-node")


class ProcessResponse(BaseModel):
    node_id: str
    request_id: str
    status: str
    issues: list[str]
    metrics: Dict[str, Any]


@app.post("/process", response_model=ProcessResponse)
async def process_payload(payload: dict) -> ProcessResponse:
    try:
        data = load_payload(payload)
    except ValueError as exc:
        logger.error(f"Invalid payload received: {exc}")
        metrics.record_request(success=False, failure_reason="invalid_payload")
        raise HTTPException(status_code=422, detail=str(exc))

    if data.validation.status != "captured":
        metrics.record_request(success=False, warnings=len(data.validation.issues), failure_reason=", ".join(data.validation.issues))
        logger.warning(f"Payload review required: {data.request_id} issues={data.validation.issues}")
    else:
        metrics.record_request(success=True)
        logger.info(f"Payload accepted: {data.request_id}")

    return ProcessResponse(
        node_id=NODE_ID,
        request_id=data.request_id,
        status=data.validation.status,
        issues=data.validation.issues,
        metrics=metrics.summary(),
    )


@app.get("/health")
async def health_check() -> dict:
    return {
        "node_id": NODE_ID,
        "status": "healthy",
        "processed_requests": metrics.total_requests,
        "error_rate": metrics.error_rate,
    }

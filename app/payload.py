import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from typing import Any, Dict, List, Optional


class CaptureRegion(BaseModel):
    region_id: str
    bounds: Dict[str, int]
    confidence: float
    area: int
    aspect_ratio: float
    image_summary: str


class ValidationInfo(BaseModel):
    status: str
    issues: List[str] = Field(default_factory=list)
    recommended_action: Optional[str] = None


class LicensePlatePayload(BaseModel):
    request_id: str
    node_id: str
    timestamp: str
    capture: CaptureRegion
    validation: ValidationInfo
    metadata: Dict[str, Any]


def build_payload(node_id: str, frame_id: int, region: Dict, image_summary: str) -> LicensePlatePayload:
    capture = CaptureRegion(
        region_id=str(uuid.uuid4()),
        bounds={
            "x": region["x"],
            "y": region["y"],
            "width": region["width"],
            "height": region["height"],
        },
        confidence=round(0.75 + min(region["area"], 5000) / 10000, 4),
        area=region["area"],
        aspect_ratio=region["aspect_ratio"],
        image_summary=image_summary,
    )
    validation = validate_capture(capture)
    payload = LicensePlatePayload(
        request_id=str(uuid.uuid4()),
        node_id=node_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
        capture=capture,
        validation=validation,
        metadata={
            "frame_id": frame_id,
            "capture_type": "license_plate_region",
            "source": "synthetic_image_stream",
            "payload_version": "1.0",
        },
    )
    return payload


def validate_capture(capture: CaptureRegion) -> ValidationInfo:
    issues = []
    if capture.area < 2500:
        issues.append("capture_area_below_threshold")
    if capture.confidence < 0.80:
        issues.append("low_capture_confidence")
    if capture.bounds["width"] < 120 or capture.bounds["height"] < 30:
        issues.append("bounds_too_small_for_plate")
    if capture.aspect_ratio < 2.0 or capture.aspect_ratio > 7.0:
        issues.append("unexpected_plate_shape")

    status = "captured" if not issues else "review_required"
    recommended_action = None
    if issues:
        recommended_action = "rescan or escalate to manual review"

    return ValidationInfo(status=status, issues=issues, recommended_action=recommended_action)


def load_payload(data: Dict[str, Any]) -> LicensePlatePayload:
    try:
        return LicensePlatePayload(**data)
    except ValidationError as exc:
        raise ValueError(f"Invalid payload: {exc}") from exc

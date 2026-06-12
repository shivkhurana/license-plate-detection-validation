from app.payload import build_payload, validate_capture


def test_build_payload_has_required_fields():
    sample_region = {"x": 20, "y": 30, "width": 200, "height": 60, "area": 12000, "aspect_ratio": 3.33}
    payload = build_payload(node_id="test-node", frame_id=0, region=sample_region, image_summary="synthetic-test")

    assert payload.node_id == "test-node"
    assert payload.metadata["frame_id"] == 0
    assert payload.capture.bounds["width"] == 200
    assert payload.validation.status in {"captured", "review_required"}


def test_validate_capture_flags_small_bounds():
    bad_region = type("Region", (), {"area": 1500, "aspect_ratio": 1.1, "bounds": {"width": 80, "height": 22}})
    validation = validate_capture(bad_region)
    assert "bounds_too_small_for_plate" in validation.issues
    assert validation.status == "review_required"

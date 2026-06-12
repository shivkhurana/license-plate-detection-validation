import pytest
from app.detector import generate_synthetic_frame, detect_plate_regions


def test_detect_plate_regions_returns_regions():
    frame = generate_synthetic_frame(1)
    regions = detect_plate_regions(frame)

    assert isinstance(regions, list)
    assert len(regions) >= 1
    for region in regions:
        assert region["width"] > 0
        assert region["height"] > 0
        assert region["area"] > 0


def test_detect_plate_regions_empty_when_no_plate_like_shape():
    import numpy as np
    blank = np.full((360, 640, 3), 36, dtype=np.uint8)
    regions = detect_plate_regions(blank)
    assert isinstance(regions, list)
    assert len(regions) == 0

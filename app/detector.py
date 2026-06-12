import cv2
import numpy as np
from typing import List, Dict, Tuple


def generate_synthetic_frame(frame_id: int, width: int = 640, height: int = 360) -> np.ndarray:
    frame = np.full((height, width, 3), 36, dtype=np.uint8)
    plate_count = 1 + (frame_id % 3)

    for i in range(plate_count):
        x = 40 + (i * 180)
        y = 120
        w = 220
        h = 60
        cv2.rectangle(frame, (x, y), (x + w, y + h), (220, 220, 220), -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (40, 40, 40), 2)
        cv2.putText(frame, f"ABC{frame_id:03d}", (x + 20, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (10, 10, 10), 2)
        cv2.rectangle(frame, (x + 12, y + 10), (x + 90, y + 30), (80, 80, 80), -1)
    return frame


def detect_plate_regions(frame: np.ndarray, min_area: int = 2000, aspect_ratio_range: Tuple[float, float] = (2.0, 6.5)) -> List[Dict]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blurred, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 5))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / float(h) if h else 0
        if not (aspect_ratio_range[0] <= aspect_ratio <= aspect_ratio_range[1]):
            continue
        margin = 5
        adjusted = {
            "x": max(x - margin, 0),
            "y": max(y - margin, 0),
            "width": min(w + margin * 2, frame.shape[1] - x),
            "height": min(h + margin * 2, frame.shape[0] - y),
            "area": int(area),
            "aspect_ratio": round(aspect_ratio, 2),
        }
        regions.append(adjusted)

    regions.sort(key=lambda item: item["area"], reverse=True)
    return regions


def extract_region(frame: np.ndarray, region: Dict) -> np.ndarray:
    x = int(region["x"])
    y = int(region["y"])
    w = int(region["width"])
    h = int(region["height"])
    return frame[y : y + h, x : x + w]


def summarize_frame(frame_id: int, regions: List[Dict]) -> Dict:
    return {
        "frame_id": frame_id,
        "region_count": len(regions),
        "largest_region_area": regions[0]["area"] if regions else 0,
    }

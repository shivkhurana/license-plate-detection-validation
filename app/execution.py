import asyncio
from typing import List
from app.detector import generate_synthetic_frame, detect_plate_regions
from app.payload import build_payload
from app.router import route_payload, available_nodes
from app.logger import configure_logger, MetricsTracker

logger = configure_logger()
metrics = MetricsTracker()


def build_stream_batch(batch_size: int = 20) -> List[dict]:
    frames = []
    for frame_id in range(batch_size):
        frame = generate_synthetic_frame(frame_id)
        regions = detect_plate_regions(frame)
        frames.append({"frame_id": frame_id, "frame": frame, "regions": regions})
    return frames


async def process_frame(frame_data: dict, node_id: str) -> None:
    frame_id = frame_data["frame_id"]
    regions = frame_data["regions"]
    if not regions:
        logger.warning(f"No regions detected in frame {frame_id}")
        metrics.record_request(success=False, failure_reason="no_regions_detected")
        return

    payload = build_payload(node_id=node_id, frame_id=frame_id, region=regions[0], image_summary=f"synthetic-frame-{frame_id:04d}")
    result = await route_payload(payload)

    if result.get("status") == "routing_failure":
        metrics.record_request(success=False, failure_reason="routing_failure")
    elif result.get("status") == "captured":
        metrics.record_request(success=True)
    else:
        metrics.record_request(success=False, warnings=len(result.get("issues", [])), failure_reason=", ".join(result.get("issues", [])))


async def run_detection_cycle(batch_size: int = 15) -> None:
    logger.info("Starting detection and routing cycle")
    nodes = available_nodes()
    stream_batch = build_stream_batch(batch_size)
    tasks = []
    for frame_data in stream_batch:
        node_id = nodes[frame_data["frame_id"] % len(nodes)].split("/")[2]
        tasks.append(process_frame(frame_data, node_id))
    await asyncio.gather(*tasks)
    logger.info("Detection cycle complete")
    logger.info(f"Metrics summary: {metrics.summary()}")

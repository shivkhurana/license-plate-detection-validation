import itertools
from typing import List
import httpx
from app.payload import LicensePlatePayload
from app.logger import configure_logger

logger = configure_logger()

NODE_URLS = [
    "http://localhost:8001/process",
    "http://localhost:8002/process",
    "http://localhost:8003/process",
    "http://localhost:8004/process",
    "http://localhost:8005/process",
]

_round_robin = itertools.cycle(NODE_URLS)


def get_next_node() -> str:
    return next(_round_robin)


async def route_payload(payload: LicensePlatePayload, timeout: float = 2.5) -> dict:
    node_url = get_next_node()
    data = payload.model_dump()
    logger.info(f"Routing payload {payload.request_id} to {node_url}")

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(node_url, json=data)
            response.raise_for_status()
            logger.info(f"Routed to {node_url} successfully")
            return response.json()
        except Exception as exc:
            logger.error(f"Routing failure to {node_url}: {exc}")
            return {
                "node_url": node_url,
                "status": "routing_failure",
                "error": str(exc),
            }


def available_nodes() -> List[str]:
    return NODE_URLS.copy()

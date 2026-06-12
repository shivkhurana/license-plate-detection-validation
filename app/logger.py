import logging
from dataclasses import dataclass, field
from typing import List


def configure_logger() -> logging.Logger:
    logger = logging.getLogger("license_plate_system")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


@dataclass
class MetricsTracker:
    total_requests: int = 0
    successful_captures: int = 0
    failed_captures: int = 0
    validation_warnings: int = 0
    edge_failures: List[str] = field(default_factory=list)

    def record_request(self, success: bool, warnings: int = 0, failure_reason: str | None = None) -> None:
        self.total_requests += 1
        if success:
            self.successful_captures += 1
        else:
            self.failed_captures += 1
        self.validation_warnings += warnings
        if failure_reason:
            self.edge_failures.append(failure_reason)

    @property
    def error_rate(self) -> float:
        return round(self.failed_captures / self.total_requests, 4) if self.total_requests else 0.0

    @property
    def warning_rate(self) -> float:
        return round(self.validation_warnings / self.total_requests, 4) if self.total_requests else 0.0

    def summary(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "successful_captures": self.successful_captures,
            "failed_captures": self.failed_captures,
            "validation_warnings": self.validation_warnings,
            "error_rate": self.error_rate,
            "warning_rate": self.warning_rate,
            "edge_failures": self.edge_failures[-10:],
        }

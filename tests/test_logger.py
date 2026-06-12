from app.logger import MetricsTracker


def test_metrics_tracker_counts_success_and_failure():
    metrics = MetricsTracker()
    metrics.record_request(success=True)
    metrics.record_request(success=False, failure_reason="no_regions_detected")

    assert metrics.total_requests == 2
    assert metrics.successful_captures == 1
    assert metrics.failed_captures == 1
    assert metrics.error_rate == 0.5
    assert "no_regions_detected" in metrics.edge_failures

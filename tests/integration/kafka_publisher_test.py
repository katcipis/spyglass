import pytest
from datetime import datetime
from datetime import timezone

from health.status import HealthStatus
from health.publishers import KafkaPublisher
from config.loaders import load_kafka_config


@pytest.mark.asyncio
async def test_kafka_publisher_publish_success():
    cfg, err = load_kafka_config()
    if err is not None:
        pytest.skip(f"test requires kafka configuration:\n{err}")
        return

    test_topic = "spyglass.integration.tests.health.status"
    publisher = KafkaPublisher(
        cfg.uri, cfg.ssl_cafile, cfg.ssl_cert, cfg.ssl_keyfile, test_topic)

    try:
        health = success_health_status()
        await publisher.start()
        await publisher.publish("http://kakfa-publisher-test", health)
    finally:
        await publisher.stop()


def success_health_status():
    return HealthStatus(
        timestamp=datetime.now(timezone.utc),
        healthy=True,
        response_time_ms=50,
        status_code=200,
        error=None,
    )
import asyncio
import pytest
from datetime import datetime
from datetime import timezone

from health.status import HealthStatus
from health.pubsub import KafkaPublisher
from health.pubsub import KafkaSubscriber
from config.loaders import load_kafka_config


@pytest.mark.asyncio
async def test_kafka_health_pubsub():
    cfg, err = load_kafka_config()
    if err is not None:
        pytest.skip(f"test requires kafka configuration:\n{err}")
        return

    test_topic = "spyglass.integration.tests.health.status"

    publisher = KafkaPublisher(
        cfg.uri, cfg.ssl_cafile, cfg.ssl_cert, cfg.ssl_keyfile, test_topic)

    subscriber = KafkaSubscriber(
        cfg.uri, cfg.ssl_cafile, cfg.ssl_cert, cfg.ssl_keyfile, test_topic)

    url = "http://kafka-publisher-test"
    health = success_health_status()
    try:
        await publisher.start()
        await publisher.publish(url, health)
    finally:
        await publisher.stop()

    test_timeout_sec = 5
    try:
        await subscriber.start()

        async def stop_subscriber():
            # WHY: subscriber can stay waiting for messages
            # for a long time in error scenarios.
            await asyncio.sleep(test_timeout_sec)
            await subscriber.stop()
            pytest.fail("timeout exceeded waiting for message on subscriber")

        task = asyncio.create_task(stop_subscriber())

        # WHY: To avoid this we need to setup/teardown unique topics
        # For now good enough is to at least find the published health
        # message, which has a timestamp that is hard to be duplicated
        # (although not impossible, so false negatives are possible).
        found_match = False
        results = []

        async for got_url, got_health_status in subscriber:
            if got_url == url and got_health_status == health:
                found_match = True
                break
            results.append((got_url, got_health_status))

        assert found_match, f"no match for '{url} {health}' on '{results}'"

    finally:
        task.cancel()
        await subscriber.stop()


def success_health_status():
    return HealthStatus(
        timestamp=datetime.now(timezone.utc),
        healthy=True,
        response_time_ms=50,
        status_code=200,
        error=None,
    )

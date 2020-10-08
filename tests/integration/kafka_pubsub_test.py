import asyncio
import pytest
from datetime import datetime
from datetime import timezone

from health.status import HealthStatus
from health.status import HealthError
from health.status import HealthErrorKind
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
    expected_messages = [
        success_health_status(),
        failure_health_status(),
    ]

    try:
        await publisher.start()
        for msg in expected_messages:
            await publisher.publish(url, msg)
    finally:
        await publisher.stop()

    test_timeout_sec = 5
    try:
        await subscriber.start()

        async def stop_subscriber():
            # WHY: subscriber can stay waiting for messages
            # for a long time in error scenarios, so we force
            # a timeout.
            await asyncio.sleep(test_timeout_sec)
            await subscriber.stop()
            pytest.fail("timeout exceeded waiting for message on subscriber")

        task = asyncio.create_task(stop_subscriber())

        # WHY: To avoid this we need to setup/teardown unique topics
        # For now good enough is to at least find the published health
        # message, which has a timestamp that is hard to be duplicated
        # (although not impossible, so false negatives are possible).
        unexpected_res = []

        async for got_url, got_health_status in subscriber:
            if got_url == url and got_health_status in expected_messages:
                expected_messages.remove(got_health_status)
                if len(expected_messages) == 0:
                    break
                continue
            unexpected_res.append((got_url, got_health_status))

        if len(expected_messages) > 0:
            e = "unable to find msgs:\n{0}\nunknown msgs:\n{1}\n".format(
                expected_messages,
                unexpected_res,
            )
            pytest.fail(e)

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


def failure_health_status():
    return HealthStatus(
        timestamp=datetime.now(timezone.utc),
        healthy=False,
        response_time_ms=50,
        status_code=400,
        error=HealthError(
            kind=HealthErrorKind.HTTP,
            details=["some detail"],
        ),
    )

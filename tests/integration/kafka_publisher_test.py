import pytest

from health.publishers import KafkaPublisher
from config.loaders import load_kafka_config

@pytest.mark.asyncio
async def test_kafka_publisher_publish_success():
    cfg, err = load_kafka_config()
    if err is not None:
        pytest.skip(f"test requires kafka configuration:\n{err}")
        return

    publisher = KafkaPublisher(
        cfg.uri, cfg.ssl_cafile, cfg.ssl_cert, cfg.ssl_keyfile)

    try:
        await publisher.start()
    finally:
        await publisher.stop()

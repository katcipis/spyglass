import json

from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context

class KafkaPublisher:
    "Publishes health check status on Kafka"

    def __init__(
        self, uri, cafile, certfile, keyfile, topic="spyglass.health.status"):
        context = create_ssl_context(
            cafile=cafile,
            certfile=certfile,
            keyfile=keyfile,
        )
        # From: https://aiokafka.readthedocs.io/en/stable/producer.html#idempotent-produce
        # Seems like the idempotency and stronger guarantees are desirable if
        # it supports the throughput. Would start with that and see how it scales.
        self.__topic = topic
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=uri,
            security_protocol="SSL",
            ssl_context=context,
            enable_idempotence=True,
        )

    async def start(self):
        await self.__producer.start()

    async def stop(self):
        await self.__producer.stop()

    async def publish(self, url, status):
        # TODO: add error handling: https://aiokafka.readthedocs.io/en/stable/api.html#error-handling
        publish_data = {
            "url": url,
            "status": {
                'timestamp': status.timestamp.isoformat(),
                'healthy': status.healthy,
                'response_time_ms': status.response_time_ms,
                'status_code': status.status_code,
            },
        }
        if status.error is not None:
            publish_data["error"] = {
                "kind": status.error.kind,
                "details": status.error.details,
            }

        serialized = json.dumps(publish_data).encode()
        await self.__producer.send_and_wait(self.__topic, serialized)

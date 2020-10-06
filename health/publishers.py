from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context

class KafkaPublisher:
    "Publishes health check status on Kafka"

    def __init__(self, bootstrap_servers, cafile, certfile, keyfile):
        context = create_ssl_context(
            cafile=cafile,
            certfile=certfile,
            keyfile=keyfile,
        )
        # From: https://aiokafka.readthedocs.io/en/stable/producer.html#idempotent-produce
        # Seems like the idempotency and stronger guarantees are desirable if
        # it supports the throughput. Would start with that and see how it scales.
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            security_protocol="SSL",
            ssl_context=context,
            enable_idempotence=True,
        )

    async def start(self):
        await self.__producer.start()

    async def stop(self):
        await self.__producer.stop()

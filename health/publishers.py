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
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            security_protocol="SSL",
            ssl_context=context,
        )

    async def start(self):
        await self.__producer.start()

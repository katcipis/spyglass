import json
import logging
import dateutil.parser
from datetime import date

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context
from aiokafka.errors import KafkaError, KafkaTimeoutError

from health.status import HealthStatus


class KafkaPublisher:
    "Publishes health check status on Kafka"

    def __init__(
      self, uri, cafile, certfile, keyfile, topic="spyglass.health.status"):

        context = create_ssl_context(
            cafile=cafile,
            certfile=certfile,
            keyfile=keyfile,
        )
        # Seems like the idempotency and stronger guarantees are desirable if
        # it supports the throughput.
        # Would start with that and see how it scales.
        self.__topic = topic
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=uri,
            security_protocol="SSL",
            ssl_context=context,
            enable_idempotence=True,
        )
        self.__log = logging.getLogger(f"{__name__}.KafkaPublisher")

    async def start(self):
        await self.__producer.start()

    async def stop(self):
        await self.__producer.stop()

    async def publish(self, url, status):
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

        msg = json.dumps(publish_data)
        try:
            self.__log.debug(f"publishing health status '{msg}' on 'self.__topic'")
            await self.__producer.send_and_wait(self.__topic, msg.encode())
            self.__log.debug(f"published '{msg}' with success")
        except KafkaTimeoutError:
            self.__log.error(f"timeout publishing status, message lost: {msg}")
        except KafkaError as err:
            errmsg = f"error: '{err}' publishing status, message lost: {msg}"
            self.__log.error(errmsg)


class KafkaSubscriber:
    "Subscribes to consume health check status on Kafka"

    def __init__(
      self, uri, cafile, certfile, keyfile, topic="spyglass.health.status"):

        context = create_ssl_context(
            cafile=cafile,
            certfile=certfile,
            keyfile=keyfile,
        )
        self.__consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=uri,
            security_protocol="SSL",
            ssl_context=context,
            group_id="spyglass-health-consumer",
        )
        self.__log = logging.getLogger(f"{__name__}.KafkaSubscriber")

    async def start(self):
        await self.__consumer.start()

    async def stop(self):
        await self.__consumer.stop()

    def __aiter__(self):
        return self

    async def __anext__(self):
        self.__log.debug("getting next health message")
        async for msg in self.__consumer:
            try:
                parsed_msg = json.loads(msg.value.decode())
                url = parsed_msg["url"]
                parsed_status = parsed_msg["status"]
                error = parsed_status.get("error", None)
                health_err = None

                if error is not None:
                    health_err = HealthStatusError(
                        kind = error["kind"],
                        details = error["details"],
                    )

                # WHY: use date-util because python datetime... is bizarre
                # stack overflow: https://bit.ly/30JwwwC
                # me isolating the issue: https://bit.ly/36IoOGO
                health_status = HealthStatus(
                    timestamp = dateutil.parser.parse(parsed_status["timestamp"]),
                    healthy = parsed_status["healthy"],
                    response_time_ms = parsed_status["response_time_ms"],
                    status_code = parsed_status["status_code"],
                    error = health_err,
                )

            except Exception as err:
                self.__log.error(f"dropping invalid '{msg}'")
                self.__log.error(f"error '{err}' parsing msg '{msg.value}'")

            self.__log.debug(f"got msg: {msg}")
            return url, health_status

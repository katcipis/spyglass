import os
import json
from collections import namedtuple

from health.checker import HealthCheck


KafkaConfig = namedtuple('KafkaConfig', [
    'uri', 'ssl_cafile', 'ssl_cert', 'ssl_keyfile'])

PostgreSQLConfig = namedtuple('PostgreSQLConfig', [ 'uri' ])


def load_kafka_config():
    """
    Loads kafka related config from the environment.

    If any configuration is missing an informational string
    is returned as a second return value, it can be used to
    provide help to the caller.
    """

    missing = []
    uri = _load_from_env(
        "SPYGLASS_KAFKA_URI",
        "URI used to connect on kafka",
        missing,
    )
    cafile = _load_from_env(
        "SPYGLASS_KAFKA_SSL_CA",
        "Path to CA file used to sign certificate",
        missing,
    )
    cert = _load_from_env(
        "SPYGLASS_KAFKA_SSL_CERT",
        "Path to signed certificate",
        missing,
    )
    privkey = _load_from_env(
        "SPYGLASS_KAFKA_SSL_KEY",
        "Path to private key file",
        missing,
    )

    if missing != []:
        errmsg = "\nMissing environment variables for Kafka config:"
        return None, errmsg + "\n\n" + "\n".join(missing)

    return KafkaConfig(
        uri=uri, ssl_cafile=cafile, ssl_cert=cert, ssl_keyfile=privkey), None


def load_health_check_config():
    missing = []
    cfgpath = _load_from_env(
        "SPYGLASS_HEALTH_CHECKS_CONFIG",
        "Path to health checks config file (JSON)",
        missing,
    )

    if missing != []:
        errmsg = "\nMissing environment variables for health checks config:"
        return None, errmsg + "\n\n" + "\n".join(missing)

    try:
        with open(cfgpath, "r") as cfgfile:
            parsed_cfg = json.loads(cfgfile.read())
            checks = []
            for probe in parsed_cfg["probes"]:
                checks.append(HealthCheck(
                    url=probe["url"],
                    period_sec=probe["period_sec"],
                    patterns=probe.get("patterns", []),
                    )
                )
            return checks, None

    except Exception as err:
        m = f"\nError reading/parsing configuration:'{cfgpath}':\n{err}\n"
        return None, m


def load_postgresql_config():
    """
    Loads postgresql related config from the environment.

    If any configuration is missing an informational string
    is returned as a second return value, it can be used to
    provide help to the caller.
    """

    missing = []
    uri = _load_from_env(
        "SPYGLASS_POSTGRESQL_URI",
        "URI used to connect on PostgreSQL",
        missing,
    )

    if missing != []:
        errmsg = "\nMissing environment variables for postgresql config:"
        return None, errmsg + "\n\n" + "\n".join(missing)

    return PostgreSQLConfig(uri=uri), None


def _load_from_env(envvar, about, missing):
    val = os.environ.get(envvar)
    if val is None:
        missing.append(envvar + " : " + about)
    return val

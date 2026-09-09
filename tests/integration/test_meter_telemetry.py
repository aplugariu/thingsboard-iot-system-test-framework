from time import time_ns

import pytest


def test_energy_meter_telemetry_reaches_platform(
    devices, mqtt_publisher, telemetry
):
    measurement = {
        "voltage": 230.4,
        "current": 10.0,
        "active_power_kw": 2.304,
    }

    with devices.managed_device("test-energy-meter") as device:
        token = devices.access_token(device.id)
        timestamp = time_ns() // 1_000_000

        mqtt_publisher.publish(token, measurement, timestamp)

        received = telemetry.wait_for_sample(
            device.id,
            keys=list(measurement),
            timestamp=timestamp,
        )

        assert received == pytest.approx(measurement)

from time import time_ns

import pytest

@pytest.mark.parametrize("energy_meter", [False], indirect=True)
def test_energy_meter_telemetry_reaches_platform(
    energy_meter, devices, mqtt_publisher, telemetry
):
    measurement = {
        "voltage": 230.4,
        "current": 10.0,
        "active_power_kw": 2.304,
    }
    token = devices.access_token(energy_meter.id)
    timestamp = time_ns() // 1_000_000

    mqtt_publisher.publish(token, measurement, timestamp)

    received = telemetry.wait_for_sample(
        energy_meter.id,
        keys=list(measurement),
        timestamp=timestamp,
    )

    assert received == pytest.approx(measurement)

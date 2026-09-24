from time import time_ns

import pytest

@pytest.mark.parametrize("energy_meter", [True], indirect=True)
def test_energy_meter_telemetry_reaches_platform(
    energy_meter,
    devices,
    device_profiles,
    mqtt_publisher,
    telemetry,
    ):  
    expected_profile = device_profiles.get_by_name("Energy Meter")
    stored_device = devices.get(energy_meter.id)

    assert stored_device.device_profile_id == expected_profile.id   
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

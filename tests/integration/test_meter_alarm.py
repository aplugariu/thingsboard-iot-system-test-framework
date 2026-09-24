from time import time_ns


def test_high_temperature_creates_critical_alarm(
    energy_meter,
    devices,
    mqtt_publisher,
    telemetry,
    alarms,
):
    temperature = 75.0
    timestamp = time_ns() // 1_000_000

    token = devices.access_token(energy_meter.id)

    mqtt_publisher.publish(
        token,
        {"temperature": temperature},
        timestamp,
    )

    received = telemetry.wait_for_sample(
        energy_meter.id,
        keys=["temperature"],
        timestamp=timestamp,
    )

    assert received["temperature"] == temperature

    alarm = alarms.wait_for_active_alarm(
        device_id=energy_meter.id,
        alarm_type="High Temperature",
        severity="CRITICAL",
    )

    assert alarm.type == "High Temperature"
    assert alarm.severity == "CRITICAL"
    assert alarm.status.startswith("ACTIVE")
    assert alarm.originator_id == energy_meter.id
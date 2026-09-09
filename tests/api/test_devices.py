def test_device_create_read_delete(devices, energy_meter):
    stored = devices.get(energy_meter.id)

    assert stored.id == energy_meter.id
    assert stored.name == energy_meter.name
    assert stored.type == "default"

    devices.delete(energy_meter.id)

    assert not devices.exists(energy_meter.id)

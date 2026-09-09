from framework.api.devices import Devices


def test_device_create_read_delete(devices: Devices):
    with devices.managed_device(name_prefix="test-energy-meter") as device:
        stored = devices.get(device.id)

        assert stored.id == device.id
        assert stored.name == device.name
        assert stored.type == "default"

        devices.delete(device.id)

        assert not devices.exists(device.id)

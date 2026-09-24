def test_device_create_read_delete(devices):
    device = devices.create("test-device")

    try:
        stored = devices.get(device.id)

        assert stored.id == device.id
        assert stored.name == device.name
        assert stored.type == "default"
    finally:
        devices.cleanup(device.id)
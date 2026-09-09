from uuid import UUID, uuid4

import httpx
import pytest


def test_device_create_read_delete(
    tenant_api_client: httpx.Client, request: pytest.FixtureRequest
):
    client = tenant_api_client
    name = f"test-energy-meter-{uuid4().hex}"
    payload = {"name": name, "type": "default"}

    created = client.post("/api/device", json=payload)
    assert created.status_code == 200, (
        f"Create failed: HTTP {created.status_code}; {created.text[:500]}"
    )

    device = created.json()
    device_id = device["id"]["id"]
    path = f"/api/device/{device_id}"

    def cleanup():
        response = client.delete(path)
        assert response.status_code in (200, 404), (
            f"Cleanup failed for {device_id}: "
            f"HTTP {response.status_code}; {response.text[:500]}"
        )

    request.addfinalizer(cleanup)

    UUID(device_id)
    assert device["id"]["entityType"] == "DEVICE"
    assert device["name"] == name

    fetched = client.get(path)
    assert fetched.status_code == 200, (
        f"Read failed for {device_id}: HTTP {fetched.status_code}"
    )
    stored = fetched.json()
    assert stored["id"]["id"] == device_id
    assert stored["name"] == name
    assert stored["type"] == "default"

    deleted = client.delete(path)
    assert deleted.status_code == 200, (
        f"Delete failed for {device_id}: HTTP {deleted.status_code}"
    )

    missing = client.get(path)
    assert missing.status_code == 404, (
        f"Expected deleted device {device_id} to return HTTP 404, "
        f"got {missing.status_code}"
    )

from contextlib import contextmanager
from dataclasses import dataclass
from uuid import uuid4

import httpx


@dataclass(frozen=True)
class Device:
    id: str
    name: str
    type: str


class Devices:
    def __init__(self, client: httpx.Client):
        self.client = client

    @staticmethod
    def _expect(response: httpx.Response, expected: int):
        if response.status_code != expected:
            raise AssertionError(
                f"{response.request.method} {response.request.url.path}: "
                f"expected HTTP {expected}, got {response.status_code}; "
                f"body: {response.text[:500]}"
            )

    def get(self, device_id: str) -> Device:
        response = self.client.get(f"/api/device/{device_id}")
        self._expect(response, 200)
        data = response.json()
        return Device(
            id=data["id"]["id"],
            name=data["name"],
            type=data["type"],
        )

    def delete(self, device_id: str):
        response = self.client.delete(f"/api/device/{device_id}")
        self._expect(response, 200)

    def exists(self, device_id: str) -> bool:
        response = self.client.get(f"/api/device/{device_id}")
        if response.status_code == 404:
            return False
        self._expect(response, 200)
        return True

    def access_token(self, device_id: str) -> str:
        response = self.client.get(f"/api/device/{device_id}/credentials")
        if response.status_code != 200:
            raise AssertionError(
                f"Cannot read credentials for {device_id}: "
                f"HTTP {response.status_code}"
            )

        credentials = response.json()
        if credentials.get("credentialsType") != "ACCESS_TOKEN":
            raise AssertionError("Device must use ACCESS_TOKEN credentials")

        token = credentials.get("credentialsId")
        if not isinstance(token, str) or not token:
            raise AssertionError("Device access token is missing")
        return token
	

    @contextmanager
    def managed_device(self, name_prefix: str, device_type: str = "default"):
        name = f"{name_prefix}-{uuid4().hex}"
        response = self.client.post(
            "/api/device",
            json={"name": name, "type": device_type},
        )
        self._expect(response, 200)
        data = response.json()
        device_id = data["id"]["id"]

        try:
            assert data["id"]["entityType"] == "DEVICE"
            assert data["name"] == name
            assert data["type"] == device_type
            yield Device(id=device_id, name=name, type=device_type)
        finally:
            if self.exists(device_id):
                self.delete(device_id)
    
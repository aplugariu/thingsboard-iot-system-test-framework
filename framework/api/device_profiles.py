from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class DeviceProfile:
    id: str
    name: str


class DeviceProfiles:
    def __init__(self, client: httpx.Client):
        self.client = client

    def get_by_name(self, name: str) -> DeviceProfile:
        response = self.client.get(
            "/api/deviceProfile/names",
            params={"activeOnly": "false"},
        )

        if response.status_code != 200:
            raise AssertionError(
                f"Device profile lookup failed: "
                f"HTTP {response.status_code}; "
                f"body: {response.text[:500]}"
            )

        profiles = response.json()

        for profile in profiles:
            if profile.get("name") == name:
                return DeviceProfile(
                    id=profile["id"]["id"],
                    name=profile["name"],
                )

        raise AssertionError(
            f"Device profile not found: {name!r}; "
            f"available={[p.get('name') for p in profiles]}"
        )
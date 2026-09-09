from time import monotonic, sleep

import httpx


class Telemetry:
    def __init__(self, client: httpx.Client):
        self.client = client

    def wait_for_sample(
        self,
        device_id: str,
        keys: list[str],
        timestamp: int,
        timeout: float = 10.0,
    ) -> dict[str, float]:
        deadline = monotonic() + timeout
        last_response = {}
        path = f"/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
        params = {
            "keys": ",".join(keys),
            "startTs": timestamp - 1,
            "endTs": timestamp + 1,
            "agg": "NONE",
            "limit": 10,
        }

        while (remaining := deadline - monotonic()) > 0:
            response = self.client.get(
                path, params=params, timeout=min(2.0, remaining)
            )
            if response.status_code != 200:
                raise AssertionError(
                    f"Telemetry read failed for {device_id}: "
                    f"HTTP {response.status_code}; {response.text[:500]}"
                )

            last_response = response.json()
            values = {}
            for key in keys:
                for sample in last_response.get(key, []):
                    if sample["ts"] == timestamp:
                        values[key] = float(sample["value"])
                        break

            if all(key in values for key in keys):
                return values

            remaining = deadline - monotonic()
            if remaining > 0:
                sleep(min(0.2, remaining))

        raise AssertionError(
            f"Telemetry not available within {timeout}s: "
            f"device={device_id}, timestamp={timestamp}, keys={keys}; "
            f"last response={last_response}"
        )

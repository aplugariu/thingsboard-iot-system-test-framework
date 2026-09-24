from dataclasses import dataclass
from time import monotonic, sleep

import httpx


@dataclass(frozen=True)
class Alarm:
    id: str
    type: str
    severity: str
    status: str
    originator_id: str


class Alarms:
    def __init__(self, client: httpx.Client):
        self.client = client

    def get_active_for_device(
        self,
        device_id: str,
        alarm_type: str,
        severity: str = "CRITICAL",
    ) -> list[Alarm]:
        response = self.client.get(
            f"/api/v2/alarm/DEVICE/{device_id}",
            params={
                "statusList": "ACTIVE",
                "severityList": severity,
                "typeList": alarm_type,
                "pageSize": 20,
                "page": 0,
                "sortProperty": "createdTime",
                "sortOrder": "DESC",
            },
        )

        if response.status_code != 200:
            raise AssertionError(
                f"Alarm lookup failed for device {device_id}: "
                f"HTTP {response.status_code}; "
                f"body: {response.text[:500]}"
            )

        alarms = []
        for item in response.json().get("data", []):
            alarms.append(
                Alarm(
                    id=item["id"]["id"],
                    type=item["type"],
                    severity=item["severity"],
                    status=item["status"],
                    originator_id=item["originator"]["id"],
                )
            )

        return alarms

    def wait_for_active_alarm(
        self,
        device_id: str,
        alarm_type: str,
        severity: str = "CRITICAL",
        timeout: float = 10.0,
    ) -> Alarm:
        deadline = monotonic() + timeout
        last_alarms = []

        while (remaining := deadline - monotonic()) > 0:
            last_alarms = self.get_active_for_device(
                device_id=device_id,
                alarm_type=alarm_type,
                severity=severity,
            )

            for alarm in last_alarms:
                if alarm.originator_id == device_id:
                    return alarm

            remaining = deadline - monotonic()
            if remaining > 0:
                sleep(min(0.2, remaining))

        raise AssertionError(
            f"Active alarm not found within {timeout}s: "
            f"device={device_id}, type={alarm_type!r}, "
            f"severity={severity}; last_alarms={last_alarms}"
        )
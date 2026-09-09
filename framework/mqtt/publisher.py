import json
from threading import Event
from uuid import uuid4

import paho.mqtt.client as mqtt


class TelemetryPublisher:
    def __init__(self, host="127.0.0.1", port=1883, timeout=10.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def publish(self, access_token: str, values: dict, timestamp: int):
        payload = json.dumps(
            {"ts": timestamp, "values": values},
            allow_nan=False,
        )
        connected = Event()
        connection_result = {}

        def on_connect(client, userdata, flags, reason_code, properties):
            connection_result["reason"] = reason_code
            connected.set()

        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"test-{uuid4().hex}",
            protocol=mqtt.MQTTv311,
            reconnect_on_failure=False,
        )
        client.username_pw_set(access_token)
        client.on_connect = on_connect
        client.connect_timeout = self.timeout

        try:
            client.connect(self.host, self.port, keepalive=30)
            client.loop_start()

            if not connected.wait(self.timeout):
                raise TimeoutError(
                    f"No MQTT connection acknowledgement from "
                    f"{self.host}:{self.port} within {self.timeout}s"
                )

            reason = connection_result["reason"]
            if reason.is_failure:
                raise AssertionError(f"MQTT connection rejected: {reason}")

            message = client.publish(
                "v1/devices/me/telemetry",
                payload=payload,
                qos=1,
                retain=False,
            )
            if message.rc != mqtt.MQTT_ERR_SUCCESS:
                raise AssertionError(
                    f"MQTT publish could not be queued: rc={message.rc}"
                )

            message.wait_for_publish(timeout=self.timeout)
            if not message.is_published():
                raise TimeoutError(
                    f"No MQTT PUBACK for message {message.mid} "
                    f"within {self.timeout}s"
                )
        finally:
            client.disconnect()
            client.loop_stop()

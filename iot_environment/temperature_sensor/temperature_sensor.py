import time
import json
import threading

from flask import Flask, jsonify
import paho.mqtt.client as mqtt


app = Flask(__name__)


temperature = 25.0


device_state = {
    "device": "temperature_sensor",
    "status": "ONLINE",
    "temperature": temperature,
    "unit": "C",
    "mqtt_connected": False
}


MQTT_BROKER = "mqtt_broker"
MQTT_PORT = 1883
MQTT_TOPIC = "building/temperature/telemetry"


mqtt_client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)


def on_connect(client, userdata, flags, reason_code, properties):

    if reason_code == 0:

        device_state["mqtt_connected"] = True

        print(
            "Temperature IoT Node connected to MQTT broker",
            flush=True
        )

    else:

        device_state["mqtt_connected"] = False

        print(
            "MQTT connection failed:",
            reason_code,
            flush=True
        )


def on_disconnect(
    client,
    userdata,
    disconnect_flags,
    reason_code,
    properties
):

    device_state["mqtt_connected"] = False

    print(
        "Temperature IoT Node disconnected from MQTT broker",
        flush=True
    )


mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect


def update_temperature():

    global temperature

    # Simulate gradual environmental temperature change
    if temperature < 28.0:
        temperature += 0.3
    else:
        temperature = 24.0

    temperature = round(temperature, 1)

    device_state["temperature"] = temperature


def publish_temperature():

    message = json.dumps({
        "device": "temperature_sensor",
        "temperature": temperature,
        "unit": "C"
    })

    result = mqtt_client.publish(
        MQTT_TOPIC,
        message
    )

    if result.rc == mqtt.MQTT_ERR_SUCCESS:

        print(
            "Published temperature:",
            message,
            flush=True
        )

    else:

        print(
            "Temperature publish failed",
            flush=True
        )


def telemetry_loop():

    while True:

        update_temperature()

        if mqtt_client.is_connected():

            publish_temperature()

        time.sleep(10)


@app.route("/")
def home():

    return jsonify({
        "device": "Temperature IoT Node",
        "status": device_state["status"],
        "communication": "MQTT"
    })


@app.route("/health")
def health():

    return jsonify(device_state)


@app.route("/temperature")
def get_temperature():

    return jsonify({
        "device": "temperature_sensor",
        "temperature": device_state["temperature"],
        "unit": "C"
    })


if __name__ == "__main__":

    print(
        "Connecting to MQTT broker...",
        flush=True
    )
    mqtt_client.username_pw_set(
    "iot_device",
    "IoTDevice@123")

    mqtt_client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60 )


    mqtt_client.loop_start()

    time.sleep(1)

    telemetry_thread = threading.Thread(
        target=telemetry_loop,
        daemon=True
    )

    telemetry_thread.start()

    app.run(
        host="0.0.0.0",
        port=5001
    )
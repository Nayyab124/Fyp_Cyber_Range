import json
import time
import paho.mqtt.client as mqtt


MQTT_BROKER = "mqtt_broker"
MQTT_PORT = 1883

TEMPERATURE_TOPIC = "building/temperature/telemetry"
LIGHT_COMMAND_TOPIC = "building/light/command"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("IoT Controller connected to MQTT broker", flush=True)

        client.subscribe(TEMPERATURE_TOPIC)

        print(
            "Subscribed to:",
            TEMPERATURE_TOPIC,
            flush=True
        )

    else:
        print(
            "MQTT connection failed:",
            reason_code,
            flush=True
        )


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(
        "IoT Controller disconnected from MQTT broker",
        flush=True
    )


def on_message(client, userdata, message):

    try:
        payload = message.payload.decode("utf-8")

        data = json.loads(payload)

        temperature = data["temperature"]

        print(
            "Received temperature:",
            temperature,
            "C",
            flush=True
        )

        # Smart-building control logic
        if temperature >= 26:
            command = "ON"
        else:
            command = "OFF"

        client.publish(
            LIGHT_COMMAND_TOPIC,
            command
        )

        print(
            "Controller sent light command:",
            command,
            flush=True
        )

    except Exception as error:

        print(
            "Controller error:",
            error,
            flush=True
        )


mqtt_client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message


if __name__ == "__main__":

    print(
        "Connecting IoT Controller to MQTT broker...",
        flush=True
    )
    mqtt_client.username_pw_set(
    "iot_device",
    "IoTDevice@123")


    mqtt_client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        60
    )

    mqtt_client.loop_start()

    time.sleep(1)

    print(
        "IoT Controller is running...",
        flush=True
    )

    while True:
        time.sleep(10)
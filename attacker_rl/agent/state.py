class AttackerState:

    def __init__(
        self,
        device_status="ONLINE",
        failed_attempts=0,
        attacker_blocked=False
    ):
        self.device_status = device_status
        self.failed_attempts = failed_attempts
        self.attacker_blocked = attacker_blocked

    def get_state(self):
        return (
            self.device_status,
            self.failed_attempts,
            self.attacker_blocked
        )
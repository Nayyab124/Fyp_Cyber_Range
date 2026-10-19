WAIT = 0
SINGLE_CREDENTIAL_ATTEMPT = 1
CREDENTIAL_BURST = 2


ACTIONS = {
    WAIT: "Wait",
    SINGLE_CREDENTIAL_ATTEMPT: "Single Credential Attempt",
    CREDENTIAL_BURST: "Credential Burst"
}


def get_action_name(action):
    return ACTIONS.get(action, "Unknown Action")
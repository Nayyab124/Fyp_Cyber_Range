WAIT_REWARD = 0

SUCCESSFUL_ATTACK_REWARD = 10

FAILED_ATTACK_PENALTY = -5

BLOCKED_ATTACK_PENALTY = -10


def calculate_reward(
    action,
    attack_successful=False,
    attacker_blocked=False
):
    if attacker_blocked:
        return BLOCKED_ATTACK_PENALTY

    if attack_successful:
        return SUCCESSFUL_ATTACK_REWARD

    if action == 0:
        return WAIT_REWARD

    return FAILED_ATTACK_PENALTY
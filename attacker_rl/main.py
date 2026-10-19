from agent.attacker_agent import AttackerAgent
from agent.rewards import calculate_reward
from attacks.credential_attack import CredentialAttack


BROKER = "mqtt_broker"
PORT = 1883

VALID_USERNAME = "iot_device"
VALID_PASSWORD = "IoTDevice@123"

TOTAL_EPISODES = 20


def run_episode(attacker, episode_number):

    print()
    print("=" * 50, flush=True)
    print("Episode:", episode_number, flush=True)
    print("=" * 50, flush=True)

    state = attacker.observe_state(
        device_status="ONLINE",
        failed_attempts=0,
        attacker_blocked=False
    )

    print(
        "State:",
        state,
        flush=True
    )

    action = attacker.choose_action(state)

    print(
        "Selected action:",
        action,
        flush=True
    )

    # --------------------------------------------------
    # ACTION 0: WAIT
    # --------------------------------------------------

    if action == 0:

        print(
            "Attacker chose: Wait",
            flush=True
        )

        attack_successful = False
        attacker_blocked = False

    # --------------------------------------------------
    # ACTION 1: SINGLE CREDENTIAL ATTEMPT
    # --------------------------------------------------

    elif action == 1:

        print(
            "Attacker chose: Single Credential Attempt",
            flush=True
        )

        attack = CredentialAttack(
            BROKER,
            PORT,
            VALID_USERNAME,
            VALID_PASSWORD
        )

        result = attack.single_attempt()

        print(
            "Credential attack result:",
            result,
            flush=True
        )

        attack_successful = result["success"]

        if attack_successful:

            command_result = attack.publish_unauthorized_command(
                "building/light/command",
                "ON"
            )

            print(
                "Unauthorized command result:",
                command_result,
                flush=True
            )

            attack_successful = command_result["success"]

        attacker_blocked = False

    # --------------------------------------------------
    # ACTION 2: CREDENTIAL BURST
    # --------------------------------------------------

    elif action == 2:

        print(
            "Attacker chose: Credential Burst",
            flush=True
        )

        credentials = [
            ("attacker", "wrongpassword"),
            ("admin", "admin123"),
            ("user", "password"),
            ("iot_device", "IoTDevice@123")
        ]

        attack = CredentialAttack(
            BROKER,
            PORT,
            "",
            ""
        )

        results = attack.credential_burst(
            credentials
        )

        print(
            "Credential burst results:",
            results,
            flush=True
        )

        attack_successful = any(
            result["success"]
            for result in results
        )

        if attack_successful:

            command_result = attack.publish_unauthorized_command(
                "building/light/command",
                "ON"
            )

            print(
                "Unauthorized command result:",
                command_result,
                flush=True
            )

            attack_successful = command_result["success"]

        attacker_blocked = False

    else:

        print(
            "Unknown action",
            flush=True
        )

        return

    # --------------------------------------------------
    # REWARD
    # --------------------------------------------------

    reward = calculate_reward(
        action,
        attack_successful,
        attacker_blocked
    )

    print(
        "Reward:",
        reward,
        flush=True
    )

    # --------------------------------------------------
    # NEXT STATE
    # --------------------------------------------------

    if action == 0:
        next_failed_attempts = 0
    else:
        next_failed_attempts = (
            0 if attack_successful else 1
        )

    next_state = attacker.observe_state(
        device_status="ONLINE",
        failed_attempts=next_failed_attempts,
        attacker_blocked=attacker_blocked
    )

    # --------------------------------------------------
    # Q-LEARNING UPDATE
    # --------------------------------------------------

    attacker.learn(
        state,
        action,
        reward,
        next_state
    )

    attacker.decay_exploration()

    print(
        "Next state:",
        next_state,
        flush=True
    )

    print(
        "Updated Q-values:",
        attacker.q_learning.q_table[state],
        flush=True
    )

    print(
        "Epsilon:",
        round(attacker.q_learning.epsilon, 4),
        flush=True
    )


def main():

    attacker = AttackerAgent()

    print(
        "RL Attacker Training Started",
        flush=True
    )

    print(
        "Total episodes:",
        TOTAL_EPISODES,
        flush=True
    )

    for episode in range(1, TOTAL_EPISODES + 1):

        run_episode(
            attacker,
            episode
        )

    print()
    print("=" * 50, flush=True)
    print("Training Completed", flush=True)
    print("=" * 50, flush=True)

    print(
        "Final Q-table:",
        attacker.q_learning.q_table,
        flush=True
    )

    print(
        "Final epsilon:",
        attacker.q_learning.epsilon,
        flush=True
    )


if __name__ == "__main__":

    main()
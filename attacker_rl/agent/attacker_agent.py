from agent.actions import (
    WAIT,
    SINGLE_CREDENTIAL_ATTEMPT,
    CREDENTIAL_BURST,
    ACTIONS
)

from agent.state import AttackerState
from learning.q_learning import QLearning


class AttackerAgent:

    def __init__(self):
        self.actions = list(ACTIONS.keys())

        self.q_learning = QLearning(
            learning_rate=0.1,
            discount_factor=0.9,
            epsilon=1.0,
            epsilon_decay=0.995,
            min_epsilon=0.01
        )

    def observe_state(
        self,
        device_status="ONLINE",
        failed_attempts=0,
        attacker_blocked=False
    ):
        state = AttackerState(
            device_status=device_status,
            failed_attempts=failed_attempts,
            attacker_blocked=attacker_blocked
        )

        return state.get_state()

    def choose_action(self, state):
        return self.q_learning.choose_action(
            state,
            self.actions
        )

    def learn(
        self,
        state,
        action,
        reward,
        next_state
    ):
        self.q_learning.update(
            state,
            action,
            reward,
            next_state,
            self.actions
        )

    def decay_exploration(self):
        self.q_learning.decay_epsilon()
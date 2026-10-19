import random


class QLearning:

    def __init__(
        self,
        learning_rate=0.1,
        discount_factor=0.9,
        epsilon=1.0,
        epsilon_decay=0.995,
        min_epsilon=0.01
    ):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon

        self.q_table = {}

    def get_q_values(self, state, actions):
        if state not in self.q_table:
            self.q_table[state] = {}

            for action in actions:
                self.q_table[state][action] = 0.0

        return self.q_table[state]

    def choose_action(self, state, actions):
        q_values = self.get_q_values(state, actions)

        # Exploration
        if random.random() < self.epsilon:
            return random.choice(actions)

        # Exploitation
        max_q = max(q_values.values())

        best_actions = [
            action
            for action, value in q_values.items()
            if value == max_q
        ]

        return random.choice(best_actions)

    def update(self, state, action, reward, next_state, actions):
        current_q_values = self.get_q_values(state, actions)
        next_q_values = self.get_q_values(next_state, actions)

        current_q = current_q_values[action]
        max_next_q = max(next_q_values.values())

        new_q = current_q + self.learning_rate * (
            reward
            + self.discount_factor * max_next_q
            - current_q
        )

        self.q_table[state][action] = new_q

    def decay_epsilon(self):
        self.epsilon = max(
            self.min_epsilon,
            self.epsilon * self.epsilon_decay
        )
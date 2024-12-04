import numpy as np

Q_TABLE_LOCATION = "./q_table/"

REWARD_CORRECT_MOVE = 1          # Positive reward for a valid move
REWARD_INCORRECT_MOVE = -10      # Negative reward for an invalid move e.g.: moving against a wall
REWARD_DEATH = -1000             # Large negative reward for dying
REWARD_SUICIDE = -1500           # Larger negative reward for committing suicide
REWARD_KILL = 1000               # Large positive reward for killing another agent
REWARD_DESTROY_OBJECT = 50       # Positive reward for destroying an object


class QLearningAgent:
    def __init__(self, state_size, action_size, alpha=0.1, gamma=0.9, epsilon=0.9, agent_id=0):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = np.zeros((state_size, action_size))  # Q-Table
        self.alpha = alpha  # Taux d'apprentissage 0.01 0.1
        self.gamma = gamma  # Facteur de réduction 0.9 0.99
        self.epsilon = epsilon  # Taux d'exploration start at 1 then decay
        self.agent_id = agent_id  # Identifiant de l'agent

    def choose_action(self, state):
        """Choisit une action basée sur la politique epsilon-greedy."""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.action_size)  # Action aléatoire
        return np.argmax(self.q_table[state])  # Action optimale

    def update(self, state, action, reward, next_state):
        """Met à jour la Q-Table avec la règle Q-Learning."""
        best_next_action = np.max(self.q_table[next_state])
        self.q_table[state, action] += self.alpha * (
            reward + self.gamma * best_next_action - self.q_table[state, action]
        )

    def save_q_table(self, filename):
        """Sauvegarde la Q-Table dans un fichier."""
        np.save(Q_TABLE_LOCATION + filename, self.q_table)

    def load_q_table(self, filename):
        """Charge la Q-Table depuis un fichier."""
        try:
            self.q_table = np.load(Q_TABLE_LOCATION + filename)
            print(f"Q-Table chargée depuis {filename}")
            #print(self.q_table)
        except FileNotFoundError:
            print(f"Fichier {filename} introuvable. Utilisation d'une nouvelle Q-Table.")

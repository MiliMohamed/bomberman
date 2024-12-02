import numpy as np

Q_TABLE_LOCATION = "./q_table/"

class QLearningAgent:
    def __init__(self, state_size, action_size, alpha=0.3, gamma=0.7, epsilon=0.1, agent_id=0):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = np.zeros((state_size, action_size))  # Q-Table
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur de réduction
        self.epsilon = epsilon  # Taux d'exploration
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
            print(self.q_table)
        except FileNotFoundError:
            print(f"Fichier {filename} introuvable. Utilisation d'une nouvelle Q-Table.")

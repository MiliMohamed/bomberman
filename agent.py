#import numpy as np
from qtable import QTable, ACTIONS
import pickle
from random import *


Q_TABLE_LOCATION = "./q_table/"

REWARD_CORRECT_MOVE = 0          # Positive reward for a valid move
REWARD_INCORRECT_MOVE = -100      # Negative reward for an invalid move e.g.: moving against a wall
REWARD_DEATH = -1000             # Large negative reward for dying
REWARD_SUICIDE = 0 # -1500           # Larger negative reward for committing suicide
REWARD_KILL = 100               # Large positive reward for killing another agent
REWARD_DESTROY_OBJECT = 5       # Positive reward for destroying an object


class QLearningAgent:
    def __init__(self, state_size, action_size, alpha=0.95, gamma=0.5, epsilon=1, agent_id=0):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = QTable()
        self.alpha = alpha  # Taux d'apprentissage 0.01 0.1
        self.gamma = gamma  # Facteur de réduction 0.9 0.99
        self.epsilon = epsilon  # Taux d'exploration start at 1 then decay
        self.agent_id = agent_id  # Identifiant de l'agent
        self.history = []

    def choose_action(self, state):
        """Choisit une action basée sur la politique epsilon greedy."""
        if random() < self.epsilon:
            self.epsilon *= 0.999
            return choice(ACTIONS)
        else:
            return self.q_table.best_action(state)

    def update(self, state, action, reward, next_state):
        """Met à jour la Q-Table avec la règle Q-Learning."""
        # best_next_action = self.q_table.best_action(self)
        # if state not in self.q_table[]:
        #     self.q_table[state] = {}
        # self.q_table[state][action] += self.alpha * (
        #     reward + self.gamma * best_next_action - self.q_table[state, action]
        # )

        self.q_table.set(state, action, reward, next_state)

        # best_next_action = self.q_table.best_action(self)
        # if state not in self.q_table:
        #     self.q_table[state] = {}
        # self.q_table[state][action] += self.alpha * (
        #      reward + self.gamma * best_next_action - self.q_table[state, action]
        # )

    def save_q_table(self, filename):
        with open(Q_TABLE_LOCATION + filename, 'wb') as file:
            pickle.dump((self.q_table.dic, self.history), file)

    def load_q_table(self, filename):
        try:
            with open(Q_TABLE_LOCATION + filename, 'rb') as file:
                self.q_table.dic, self.history = pickle.load(file)
        except FileNotFoundError:
            print(f"Fichier {filename} introuvable. Utilisation d'une nouvelle Q-Table.")

from random import *

ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "PLACE_BOMB", "WAIT"]


def arg_max(table):
    return max(table, key=table.get)


class QTable:
    def __init__(self, learning_rate=0.9, discount_factor=0.9):
        self.dic = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor

    def set(self, state, action, reward, new_state):
        if state not in self.dic:
            self.dic[state] = {ACTIONS[0]: 0, ACTIONS[1]: 0, ACTIONS[2]: 0, ACTIONS[3]: 0, ACTIONS[4]: 0, ACTIONS[5]: 0}
        if new_state not in self.dic:
            self.dic[new_state] = {ACTIONS[0]: 0, ACTIONS[1]: 0, ACTIONS[2]: 0, ACTIONS[3]: 0, ACTIONS[4]: 0, ACTIONS[5]: 0}

        self.dic[state][action] += reward

        delta = reward + self.discount_factor * max(self.dic[new_state].values()) - self.dic[state][action]
        self.dic[state][action] += self.learning_rate * delta
        # Q(s, a) = Q(s, a) + alpha * [reward + gamma * max(S', a) - Q(s, a)]

    def best_action(self, position):
        if position in self.dic:
            return arg_max(self.dic[position])
        else:
            return choice(ACTIONS)

    def __repr__(self):
        res = " U  D  L  F  P  "
        for action in ACTIONS:
            res += f'{action:15s}'
        res += '\r\n'
        for state in self.dic:
            res += str(state) + " "
            for action in self.dic[state]:
                res += f"{self.dic[state][action]:15f}"
            res += '\r\n'
        return res

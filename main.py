import arcade
import random
import numpy as np

# Dimensions de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 40
ROWS = SCREEN_HEIGHT // CELL_SIZE
COLS = SCREEN_WIDTH // CELL_SIZE

# Types de cellules
EMPTY = 0
DESTRUCTIBLE = 1
INDESTRUCTIBLE = 2
ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "PLACE_BOMB"]


class QLearningAgent:
    def __init__(self, state_size, action_size, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = np.zeros((state_size, action_size))  # Q-Table
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur de réduction
        self.epsilon = epsilon  # Taux d'exploration

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


class BombermanGame(arcade.Window):
    def __init__(self, num_agents=2):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Bomberman - Multi-Agent Training")
        arcade.set_background_color(arcade.color.BLACK)

        self.num_agents = num_agents  # Nombre d'agents
        self.grid = []  # Grille du jeu
        self.agent_positions = []  # Liste des positions des agents
        self.bombs = []  # Liste des bombes
        self.scores = [0] * num_agents  # Scores des agents
        self.episodes = 0  # Nombre d'épisodes d'entraînement
        self.exit_position = (ROWS - 1, COLS - 1)  # Position de la sortie
        self.game_won = False  # Indique si le jeu a été gagné

        # Initialiser les agents Q-Learning
        self.agents = [
            QLearningAgent(state_size=ROWS * COLS, action_size=len(ACTIONS))
            for _ in range(num_agents)
        ]

    def setup(self):
        """Initialisation du jeu."""
        # Générer la grille
        self.grid = []
        for row in range(ROWS):
            row_data = []
            for col in range(COLS):
                if random.random() < 0.2:
                    row_data.append(DESTRUCTIBLE if random.random() < 0.7 else INDESTRUCTIBLE)
                else:
                    row_data.append(EMPTY)
            self.grid.append(row_data)

        # Initialiser les positions des agents
        self.agent_positions = [(1, 1 + i * 3) for i in range(self.num_agents)]
        self.scores = [0] * self.num_agents
        self.bombs = []
        self.grid[self.exit_position[0]][self.exit_position[1]] = EMPTY  # Assurez-vous que la sortie est accessible
        self.game_won = False

    def get_state(self, agent_index):
        """Convertit la position actuelle d'un agent en un état unique."""
        row, col = self.agent_positions[agent_index]
        return row * COLS + col

    def perform_action(self, agent_index, action):
        """Effectue une action pour un agent."""
        row, col = self.agent_positions[agent_index]

        if action == 0 and row > 0 and self.grid[row - 1][col] == EMPTY:  # UP
            self.agent_positions[agent_index] = (row - 1, col)
            return 5  # Récompense pour mouvement valide
        elif action == 1 and row < ROWS - 1 and self.grid[row + 1][col] == EMPTY:  # DOWN
            self.agent_positions[agent_index] = (row + 1, col)
            return 5
        elif action == 2 and col > 0 and self.grid[row][col - 1] == EMPTY:  # LEFT
            self.agent_positions[agent_index] = (row, col - 1)
            return 5
        elif action == 3 and col < COLS - 1 and self.grid[row][col + 1] == EMPTY:  # RIGHT
            self.agent_positions[agent_index] = (row, col + 1)
            return 5
        elif action == 4:  # PLACE_BOMB
            self.bombs.append({"row": row, "col": col, "timer": 3})
            return 0  # Pas de récompense immédiate pour poser une bombe
        return -1  # Récompense négative pour une action invalide

    def on_draw(self):
        """Affiche la grille et les statistiques."""
        self.clear()

        # Affichage de la grille
        for row in range(ROWS):
            for col in range(COLS):
                x = col * CELL_SIZE + CELL_SIZE // 2
                y = row * CELL_SIZE + CELL_SIZE // 2

                if self.grid[row][col] == DESTRUCTIBLE:
                    arcade.draw_text("D", x, y, arcade.color.RED, font_size=20, anchor_x="center", anchor_y="center")
                elif self.grid[row][col] == INDESTRUCTIBLE:
                    arcade.draw_text("I", x, y, arcade.color.GRAY, font_size=20, anchor_x="center", anchor_y="center")
                elif (row, col) == self.exit_position:
                    arcade.draw_text("E", x, y, arcade.color.GOLD, font_size=20, anchor_x="center", anchor_y="center")
                else:
                    arcade.draw_text(".", x, y, arcade.color.WHITE, font_size=20, anchor_x="center", anchor_y="center")

        # Afficher les positions des agents
        for i, (row, col) in enumerate(self.agent_positions):
            x = col * CELL_SIZE + CELL_SIZE // 2
            y = row * CELL_SIZE + CELL_SIZE // 2
            color = arcade.color.BLUE if i == 0 else arcade.color.GREEN
            arcade.draw_text(f"A{i+1}", x, y, color, font_size=20, anchor_x="center", anchor_y="center")

        # Affichage des bombes
        for bomb in self.bombs:
            x = bomb["col"] * CELL_SIZE + CELL_SIZE // 2
            y = bomb["row"] * CELL_SIZE + CELL_SIZE // 2
            arcade.draw_text("B", x, y, arcade.color.YELLOW, font_size=20, anchor_x="center", anchor_y="center")

        # Statistiques
        for i, score in enumerate(self.scores):
            arcade.draw_text(f"Agent {i+1} - Score: {score}", 10, SCREEN_HEIGHT - 30 * (i + 1),
                             arcade.color.GREEN, font_size=20)

        # Message de victoire
        if self.game_won:
            arcade.draw_text("VICTORY! An agent reached the exit!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                             arcade.color.GOLD, font_size=30, anchor_x="center")

    def on_update(self, delta_time):
        """Met à jour l'état du jeu."""
        if self.game_won:
            return  # Ne rien faire si le jeu est gagné

        # Mise à jour des bombes
        for bomb in self.bombs[:]:
            bomb["timer"] -= delta_time
            if bomb["timer"] <= 0:
                self.explode_bomb(bomb)
                self.bombs.remove(bomb)

        # Mettre à jour chaque agent
        for i in range(self.num_agents):
            current_state = self.get_state(i)
            action = self.agents[i].choose_action(current_state)
            reward = self.perform_action(i, action)
            reward += self.calculate_reward(i)
            next_state = self.get_state(i)
            self.agents[i].update(current_state, action, reward, next_state)

            # Vérification si un agent a atteint la sortie
            if self.agent_positions[i] == self.exit_position:
                self.game_won = True
                print(f"Agent {i + 1} a atteint la sortie ! Jeu terminé.")
                return

    def calculate_reward(self, agent_index):
        """Calcule une récompense basée sur l'état actuel pour un agent."""
        row, col = self.agent_positions[agent_index]
        reward = 0

        if self.grid[row][col] == DESTRUCTIBLE:
            self.grid[row][col] = EMPTY
            self.scores[agent_index] += 10
            reward += 10
        elif self.grid[row][col] == INDESTRUCTIBLE:
            reward -= 10  # Pénalité pour toucher un mur indestructible

        return reward

    def explode_bomb(self, bomb):
        """Gère l'explosion d'une bombe."""
        row, col = bomb["row"], bomb["col"]
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            for i in range(1, 3):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < ROWS and 0 <= c < COLS:
                    if self.grid[r][c] == INDESTRUCTIBLE:
                        break
                    elif self.grid[r][c] == DESTRUCTIBLE:
                        self.grid[r][c] = EMPTY
                        break


if __name__ == "__main__":
    game = BombermanGame(num_agents=2)
    game.setup()
    arcade.run()

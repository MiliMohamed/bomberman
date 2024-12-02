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
ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "PLACE_BOMB", "WAIT"]


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
        np.save(filename, self.q_table)

    def load_q_table(self, filename):
        """Charge la Q-Table depuis un fichier."""
        try:
            self.q_table = np.load(filename)
            print(f"Q-Table chargée depuis {filename}")
            print(self.q_table)
        except FileNotFoundError:
            print(f"Fichier {filename} introuvable. Utilisation d'une nouvelle Q-Table.")


class BombermanGame(arcade.Window):
    def __init__(self, num_agents=4, max_episodes=1000):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Bomberman - Multi-Agent Training")
        arcade.set_background_color(arcade.color.BLACK)

        self.num_agents = num_agents
        self.grid = []
        self.agent_positions = []
        self.bombs = []
        self.scores = [0] * num_agents
        self.lives = [3] * num_agents
        self.game_over = [False] * num_agents  # Initialize as a list
        self.current_episode = 0
        self.max_episodes = max_episodes
        self.time_accumulator = 0  # Pour ralentir la vitesse du jeu
        self.update_interval = 0.3  # Temps entre chaque mise à jour (en secondes)

        # Initialiser les agents Q-Learning
        self.agents = [
            QLearningAgent(state_size=ROWS * COLS, action_size=len(ACTIONS), agent_id=i)
            for i in range(num_agents)
        ]

        # Charger les Q-Tables si disponibles
        for i, agent in enumerate(self.agents):
            agent.load_q_table(f"agent_{i+1}_qtable.npy")

    def setup(self):
        """Initialisation du jeu."""
        self.grid = []

        # Define a "buffer zone" around agent spawn positions (for example, 3x3 area around each spawn point)
        buffer_zone_size = 1

        # Create the grid with obstacles while leaving space around the agent spawn points
        for row in range(ROWS):
            row_data = []
            for col in range(COLS):
                # Set a condition for leaving empty space around spawn points
                if any(
                        (row >= spawn_row - buffer_zone_size and row <= spawn_row + buffer_zone_size and
                         col >= spawn_col - buffer_zone_size and col <= spawn_col + buffer_zone_size)
                        for spawn_row, spawn_col in self.agent_positions
                ):
                    row_data.append(EMPTY)  # Leave space around spawn points
                elif random.random() < 0.2:
                    row_data.append(DESTRUCTIBLE if random.random() < 0.7 else INDESTRUCTIBLE)
                else:
                    row_data.append(EMPTY)
            self.grid.append(row_data)

        # Spawn agents in the corners but leave a buffer zone
        corners = [(0, 0), (0, COLS - 1), (ROWS - 1, 0), (ROWS - 1, COLS - 1)]
        self.agent_positions = []

        # Assign each agent to a corner while ensuring the buffer zone is respected
        for i in range(self.num_agents):
            corner = corners[i % len(corners)]  # This ensures we reuse corners if more than 4 agents
            self.agent_positions.append(corner)

            # Ensure a buffer zone around each spawn position (mark the grid with empty space)
            for r in range(corner[0] - buffer_zone_size, corner[0] + buffer_zone_size + 1):
                for c in range(corner[1] - buffer_zone_size, corner[1] + buffer_zone_size + 1):
                    if 0 <= r < ROWS and 0 <= c < COLS:
                        self.grid[r][c] = EMPTY  # Clear any obstacles in the buffer zone

        self.scores = [0] * self.num_agents
        self.lives = [1] * self.num_agents
        self.bombs = []
        self.game_over = [False] * self.num_agents  # Reset game_over list

    def get_state(self, agent_index):
        """Convertit la position actuelle d'un agent en un état unique."""
        row, col = self.agent_positions[agent_index]
        return row * COLS + col

    def perform_action(self, agent_index, action):
        """Effectue une action pour un agent."""
        if self.game_over[agent_index]:
            return -1000  # Pénalité pour agent mort

        row, col = self.agent_positions[agent_index]

        if action == 0 and row > 0 and self.grid[row - 1][col] == EMPTY:  # UP
            self.agent_positions[agent_index] = (row - 1, col)
            self.scores[agent_index] -= 1
            return -1  # Récompense pour mouvement valide
        elif action == 1 and row < ROWS - 1 and self.grid[row + 1][col] == EMPTY:  # DOWN
            self.agent_positions[agent_index] = (row + 1, col)
            self.scores[agent_index] -= 1
            return -1
        elif action == 2 and col > 0 and self.grid[row][col - 1] == EMPTY:  # LEFT
            self.agent_positions[agent_index] = (row, col - 1)
            self.scores[agent_index] -= 1
            return -1
        elif action == 3 and col < COLS - 1 and self.grid[row][col + 1] == EMPTY:  # RIGHT
            self.agent_positions[agent_index] = (row, col + 1)
            self.scores[agent_index] -= 1
            return -1
        elif action == 4:  # PLACE_BOMB
            self.bombs.append({"row": row, "col": col, "timer": 3, "owner": agent_index})
            self.scores[agent_index] -= 10
            return -10
        elif action == 5:
            self.agent_positions[agent_index] = (row, col)
            self.scores[agent_index] -= 1
            return -1
        return -10  # Récompense négative pour une action invalide

    def explode_bomb(self, bomb):
        """Gère l'explosion d'une bombe."""
        row, col = bomb["row"], bomb["col"]
        affected_positions = [(row, col)]  # Add the bomb's position as affected

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            for i in range(1, 3):  # Explosion range
                r, c = row + dr * i, col + dc * i
                if 0 <= r < ROWS and 0 <= c < COLS:
                    if self.grid[r][c] == INDESTRUCTIBLE:
                        break
                    affected_positions.append((r, c))
                    if self.grid[r][c] == DESTRUCTIBLE:
                        self.grid[r][c] = EMPTY
                        break

        # Mark affected positions for explosions
        self.explosion_positions = affected_positions

        # Apply damage to agents in affected positions
        for i, (arow, acol) in enumerate(self.agent_positions):
            if (arow, acol) in affected_positions and not self.game_over[i]:
                self.lives[i] -= 1
                self.scores[i] -= 1000
                print(f"Agent {i+1} died in an explosion")
                if self.lives[i] <= 0:
                    self.game_over[i] = True

    def count_active_agents(self):
        """Compte le nombre d'agents encore en vie."""
        return sum(1 for life in self.lives if life > 0)

    def on_draw(self):
        """Affiche la grille et les statistiques."""
        self.clear()

        # Clear explosion positions at the start of each frame
        self.explosion_positions = []

        for row in range(ROWS):
            for col in range(COLS):
                x = col * CELL_SIZE + CELL_SIZE // 2
                y = row * CELL_SIZE + CELL_SIZE // 2
                if self.grid[row][col] == DESTRUCTIBLE:
                    arcade.draw_rectangle_filled(x, y, CELL_SIZE, CELL_SIZE, arcade.color.RED)
                elif self.grid[row][col] == INDESTRUCTIBLE:
                    arcade.draw_rectangle_filled(x, y, CELL_SIZE, CELL_SIZE, arcade.color.GRAY)
                else:
                    arcade.draw_rectangle_filled(x, y, CELL_SIZE, CELL_SIZE, arcade.color.BLACK)
                    arcade.draw_rectangle_outline(x, y, CELL_SIZE, CELL_SIZE, arcade.color.WHITE)

        for i, (row, col) in enumerate(self.agent_positions):
            if not self.game_over[i]:
                x = col * CELL_SIZE + CELL_SIZE // 2
                y = row * CELL_SIZE + CELL_SIZE // 2
                color = arcade.color.BLUE if i == 0 else arcade.color.GREEN
                arcade.draw_circle_filled(x, y, CELL_SIZE // 3, color)

        # Draw bombs
        for bomb in self.bombs:
            x = bomb["col"] * CELL_SIZE + CELL_SIZE // 2
            y = bomb["row"] * CELL_SIZE + CELL_SIZE // 2
            color = bomb.get("color",
                             arcade.color.ASH_GREY)  # Default to gray, change to orange and red before explosion
            arcade.draw_circle_filled(x, y, CELL_SIZE // 4, color)

        # Draw red diamonds on explosion positions for this frame only
        for (row, col) in self.explosion_positions:
            x = col * CELL_SIZE + CELL_SIZE // 2
            y = row * CELL_SIZE + CELL_SIZE // 2
            arcade.draw_polygon_filled(
                [(x, y - CELL_SIZE // 4), (x + CELL_SIZE // 4, y), (x, y + CELL_SIZE // 4), (x - CELL_SIZE // 4, y)],
                arcade.color.RED
            )

        # Draw scores and lives
        for i, (score, lives) in enumerate(zip(self.scores, self.lives)):
            arcade.draw_text(f"Agent {i + 1} - Score: {score}, Lives: {lives}",
                             10, SCREEN_HEIGHT - 20 * (i + 1), arcade.color.WHITE, font_size=12)

    def on_update(self, delta_time):
        """Met à jour l'état du jeu."""
        self.time_accumulator += delta_time
        if self.time_accumulator < self.update_interval:
            return
        self.time_accumulator = 0

        for bomb in self.bombs[:]:
            bomb["timer"] -= self.update_interval
            if bomb["timer"] <= 2:  # Change bomb color to orange just before red
                bomb["color"] = arcade.color.ORANGE  # Change to orange
            if bomb["timer"] <= 1:  # Change to red just before explosion
                bomb["color"] = arcade.color.RED  # Change to red
            if bomb["timer"] <= 0:
                self.explode_bomb(bomb)
                self.bombs.remove(bomb)

        for i in range(self.num_agents):
            if self.game_over[i]:
                continue
            current_state = self.get_state(i)
            action = self.agents[i].choose_action(current_state)
            reward = self.perform_action(i, action)
            next_state = self.get_state(i)
            self.agents[i].update(current_state, action, reward, next_state)

        # Check if exactly one agent has game_over == False or if all agents are game_over == True
        if self.game_over.count(False) == 1 or all(self.game_over):
            print(f"Épisode {self.current_episode + 1} terminé. Réinitialisation du jeu.")
            self.current_episode += 1
            for i, agent in enumerate(self.agents):
                agent.save_q_table(f"agent_{i + 1}_qtable.npy")
            self.setup()


if __name__ == "__main__":
    game = BombermanGame(num_agents=4)
    game.setup()
    print()
    arcade.run()

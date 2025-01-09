import arcade
import random
from agent import QLearningAgent, REWARD_DEATH, REWARD_CORRECT_MOVE, REWARD_INCORRECT_MOVE, REWARD_SUICIDE, REWARD_KILL, \
    REWARD_DESTROY_OBJECT
from bomb import Bomb

MAP_FILE_1 = "./map/map_1"

# Dimensions de la fenêtre
SCREEN_WIDTH = 840
SCREEN_HEIGHT = 600
CELL_SIZE = 40 # 40 default
#ROWS = SCREEN_HEIGHT // CELL_SIZE
#COLS = SCREEN_WIDTH // CELL_SIZE
ROWS = open(MAP_FILE_1).read().count('\n')+1
COLS = 21

# Types de cellules
EMPTY = 0
DESTRUCTIBLE = 1
INDESTRUCTIBLE = 2
BOMB = 3
ITEM = 4
ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "PLACE_BOMB", "WAIT"]


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
        self.update_interval = 0.01  # Temps entre chaque mise à jour (en secondes)

        # Initialiser les agents Q-Learning
        self.agents = [
            QLearningAgent(state_size=ROWS * COLS * 5**4, action_size=len(ACTIONS), agent_id=i)
            for i in range(num_agents)
        ]

        # Charger les Q-Tables si disponibles
        for i, agent in enumerate(self.agents):
            agent.load_q_table(f"agent_{i+1}_qtable.qtable")

    # def setup(self):
    #     """Initialisation du jeu."""
    #     self.grid = []
    #
    #     # Define a "buffer zone" around agent spawn positions (for example, 3x3 area around each spawn point)
    #     buffer_zone_size = 1
    #
    #     # Create the grid with obstacles while leaving space around the agent spawn points
    #     for row in range(ROWS):
    #         row_data = []
    #         for col in range(COLS):
    #             # Set a condition for leaving empty space around spawn points
    #             if any(
    #                     (spawn_row - buffer_zone_size <= row <= spawn_row + buffer_zone_size and
    #                      spawn_col - buffer_zone_size <= col <= spawn_col + buffer_zone_size)
    #                     for spawn_row, spawn_col in self.agent_positions
    #             ):
    #                 row_data.append(EMPTY)  # Leave space around spawn points
    #             elif random.random() < 0.2:
    #                 row_data.append(DESTRUCTIBLE if random.random() < 0.7 else INDESTRUCTIBLE)
    #             else:
    #                 row_data.append(EMPTY)
    #         self.grid.append(row_data)
    #
    #     # Spawn agents in the corners but leave a buffer zone
    #     corners = [(0, 0), (0, COLS - 1), (ROWS - 1, 0), (ROWS - 1, COLS - 1)]
    #     self.agent_positions = []
    #
    #     # Assign each agent to a corner while ensuring the buffer zone is respected
    #     for i in range(self.num_agents):
    #         corner = corners[i % len(corners)]  # This ensures we reuse corners if more than 4 agents
    #         self.agent_positions.append(corner)
    #
    #         # Ensure a buffer zone around each spawn position (mark the grid with empty space)
    #         for r in range(corner[0] - buffer_zone_size, corner[0] + buffer_zone_size + 1):
    #             for c in range(corner[1] - buffer_zone_size, corner[1] + buffer_zone_size + 1):
    #                 if 0 <= r < ROWS and 0 <= c < COLS:
    #                     self.grid[r][c] = EMPTY  # Clear any obstacles in the buffer zone
    #
    #     self.scores = [0] * self.num_agents
    #     self.lives = [1] * self.num_agents
    #     self.bombs = []
    #     self.game_over = [False] * self.num_agents  # Reset game_over list

    def setup(self):
        """Initialisation du jeu."""
        self.grid = []

        # Open the map file and read its content
        with open(MAP_FILE_1, 'r') as map_file:
            map_level = map_file.readlines()

        # Print each line of the map
        for row in map_level:
            row_data = []
            for char in row.strip():
                if char == 'I':
                    row_data.append(DESTRUCTIBLE)
                elif char == '.':
                    row_data.append(EMPTY)
                elif char == 'X':
                    row_data.append(INDESTRUCTIBLE)
                else:
                    raise ValueError(f"Invalid character '{char}' in the map file.")
            #print(row.strip())  # Use .strip() to remove the newline character at the end of each line
            self.grid.append(row_data)



        # # Define a "buffer zone" around agent spawn positions (for example, 3x3 area around each spawn point)
        # buffer_zone_size = 1
        #
        # # Create the grid with obstacles while leaving space around the agent spawn points
        # for row in range(ROWS):
        #     row_data = []
        #     for col in range(COLS):
        #         # Set a condition for leaving empty space around spawn points
        #         if any(
        #                 (spawn_row - buffer_zone_size <= row <= spawn_row + buffer_zone_size and
        #                  spawn_col - buffer_zone_size <= col <= spawn_col + buffer_zone_size)
        #                 for spawn_row, spawn_col in self.agent_positions
        #         ):
        #             row_data.append(EMPTY)  # Leave space around spawn points
        #         elif random.random() < 0.2:
        #             row_data.append(DESTRUCTIBLE if random.random() < 0.7 else INDESTRUCTIBLE)
        #         else:
        #             row_data.append(EMPTY)
        #     self.grid.append(row_data)
        #
        #
        #
        #

        # Spawn agents in the corners but leave a buffer zone
        corners = [(0, 0), (0, COLS - 1), (ROWS - 1, 0), (ROWS - 1, COLS - 1)]
        self.agent_positions = []

        # Assign each agent to a corner while ensuring the buffer zone is respected
        for i in range(self.num_agents):
            corner = corners[i % len(corners)]  # This ensures we reuse corners if more than 4 agents
            self.agent_positions.append(corner)

            # # Ensure a buffer zone around each spawn position (mark the grid with empty space)
            # for r in range(corner[0] - buffer_zone_size, corner[0] + buffer_zone_size + 1):
            #     for c in range(corner[1] - buffer_zone_size, corner[1] + buffer_zone_size + 1):
            #         if 0 <= r < ROWS and 0 <= c < COLS:
            #             self.grid[r][c] = EMPTY  # Clear any obstacles in the buffer zone

        self.scores = [0] * self.num_agents
        self.lives = [1] * self.num_agents
        self.bombs = []
        self.game_over = [False] * self.num_agents  # Reset game_over list

    # TODO add radar + align with bomb
    def get_state(self, agent_index):
        # """Convertit la position actuelle d'un agent en un état unique."""
        # row, col = self.agent_positions[agent_index]
        # #print(f"State of agent {agent_index} = {row * COLS + col}")
        # #return row * COLS + col
        # return [row, col]

        """Convert the current position of an agent into a radar view state."""
        row, col = self.agent_positions[agent_index]
        position = self.grid[row][col]

        # Define the radar range (1 for 3x3 grid)
        radar_range = 1

        if row-1 < 0:
            above = 2
        else:
            above = self.grid[row-1][col]

        if col+1 > len(self.grid):
            right = 2
        else:
            right = self.grid[row][col+1]

        if col-1 < 0:
            left = 2
        else:
            left = self.grid[row][col-1]

        if row+1 > len(self.grid[0]):
            below = 2
        else:
            below = self.grid[row+1][col]

        return (position, above, below, left, right)

        # # Initialize the radar view with the surrounding cells
        # radar_view = []
        # for dr in range(-radar_range, radar_range + 1):
        #     radar_row = []
        #     for dc in range(-radar_range, radar_range + 1):
        #         r, c = row + dr, col + dc
        #         if 0 <= r < ROWS and 0 <= c < COLS:
        #             radar_row.append(self.grid[r][c])
        #         else:
        #             radar_row.append(-1)  # Out of bounds
        #     radar_view.append(radar_row)
        # #print(f"radar view: {radar_view}")
        # return radar_view

    def perform_action(self, agent_index, action):
        """Effectue une action pour un agent."""
        if self.game_over[agent_index]:
            return REWARD_DEATH  # Pénalité pour agent mort

        if agent_index >= 1:
            return REWARD_CORRECT_MOVE

        row, col = self.agent_positions[agent_index]

        def is_cell_occupied_by_another_agent(target_row, target_col):
            for i, (other_row, other_col) in enumerate(self.agent_positions):
                if i != agent_index and (other_row, other_col) == (target_row, target_col):
                    return True
            return False

        if action == 0 and row > 0 and self.grid[row - 1][col] == EMPTY and not is_cell_occupied_by_another_agent(row - 1, col):  # UP
            self.agent_positions[agent_index] = (row - 1, col)
            self.scores[agent_index] += REWARD_CORRECT_MOVE
            return REWARD_CORRECT_MOVE  # Récompense pour mouvement valide
        elif action == 1 and row < ROWS - 1 and self.grid[row + 1][col] == EMPTY and not is_cell_occupied_by_another_agent(row + 1, col):  # DOWN
            self.agent_positions[agent_index] = (row + 1, col)
            self.scores[agent_index] += REWARD_CORRECT_MOVE
            return REWARD_CORRECT_MOVE
        elif action == 2 and col > 0 and self.grid[row][col - 1] == EMPTY and not is_cell_occupied_by_another_agent(row, col - 1):  # LEFT
            self.agent_positions[agent_index] = (row, col - 1)
            self.scores[agent_index] += REWARD_CORRECT_MOVE
            return REWARD_CORRECT_MOVE
        elif action == 3 and col < COLS - 1 and self.grid[row][col + 1] == EMPTY and not is_cell_occupied_by_another_agent(row, col + 1):  # RIGHT
            self.agent_positions[agent_index] = (row, col + 1)
            self.scores[agent_index] += REWARD_CORRECT_MOVE
            return REWARD_CORRECT_MOVE
        # elif action == 4:  # PLACE_BOMB
        #     self.bombs.append({"row": row, "col": col, "timer": 3, "owner": agent_index})
        #     self.grid[row][col] = BOMB
        #     self.scores[agent_index] -= 10
        #     return 0
        elif action == 4:
            if self.grid[row][col] == BOMB:
                return REWARD_INCORRECT_MOVE
            new_bomb = Bomb(row, col, agent_index)
            self.bombs.append(new_bomb)
            self.grid[row][col] = BOMB
            return REWARD_CORRECT_MOVE
        elif action == 5:
            self.agent_positions[agent_index] = (row, col)
            self.scores[agent_index] += REWARD_CORRECT_MOVE
            return REWARD_CORRECT_MOVE
        return REWARD_INCORRECT_MOVE  # Récompense négative pour une action invalide

    def explode_bomb(self, bomb):
        """Gère l'explosion d'une bombe."""
        row, col = bomb.row, bomb.col
        affected_positions = [(row, col)]  # Add the bomb's position as affected

        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            for i in range(1, bomb.power+1):  # Explosion range
                r, c = row + dr * i, col + dc * i
                if 0 <= r < ROWS and 0 <= c < COLS:
                    if self.grid[r][c] == INDESTRUCTIBLE:
                        break
                    affected_positions.append((r, c))
                    if self.grid[r][c] == DESTRUCTIBLE:
                        self.grid[r][c] = EMPTY
                        self.scores[bomb.owner] += REWARD_DESTROY_OBJECT
                        #print(f"Agent {bomb.owner+1} destroyed something !!! {REWARD_DESTROY_OBJECT} pts")
                        break

        # Mark affected positions for explosions
        self.explosion_positions = affected_positions

        # Apply damage to agents in affected positions
        for i, (arow, acol) in enumerate(self.agent_positions):
            if (arow, acol) in affected_positions and not self.game_over[i]:
                self.lives[i] -= 1
                self.scores[i] += REWARD_DEATH
                #print(f"Agent {i+1} died in an explosion, killed by agent {bomb.owner+1}")
                if i == bomb.owner:
                    #print(f"Agent {i+1} killed himself !!! {REWARD_SUICIDE} pts")
                    self.scores[i] += REWARD_SUICIDE
                else:
                    #print(f"Agent {i+1} got killed by agent {bomb.owner+1} !!! {REWARD_KILL} pts")
                    self.scores[bomb.owner] += REWARD_KILL

                if self.lives[i] <= 0:
                    self.game_over[i] = True

    def count_active_agents(self):
        """Compte le nombre d'agents encore en vie."""
        return sum(1 for life in self.lives if life > 0)

    # def on_draw(self):
    #     """Affiche la grille et les statistiques."""
    #     self.clear()
    #     # for bomb in self.bombs:
    #     #     print(f"Bom exploding in {bomb.timer} at {bomb.col} {bomb.row}")
    #
    #     # Clear explosion positions at the start of each frame
    #     self.explosion_positions = []
    #
    #     for row in range(ROWS):
    #         for col in range(COLS):
    #             x = col * CELL_SIZE + CELL_SIZE // 2
    #             y = row * CELL_SIZE + CELL_SIZE // 2
    #             if self.grid[row][col] == DESTRUCTIBLE:
    #                 arcade.draw_rectangle_filled(x, y, CELL_SIZE, CELL_SIZE, arcade.color.RED)
    #             elif self.grid[row][col] == INDESTRUCTIBLE:
    #                 arcade.draw_rectangle_filled(x, y, CELL_SIZE, CELL_SIZE, arcade.color.GRAY)
    #             else:
    #                 arcade.draw_rectangle_filled(x, y, CELL_SIZE, CELL_SIZE, arcade.color.BLACK)
    #                 arcade.draw_rectangle_outline(x, y, CELL_SIZE, CELL_SIZE, arcade.color.WHITE)
    #
    #     for i, (row, col) in enumerate(self.agent_positions):
    #         if not self.game_over[i]:
    #             x = col * CELL_SIZE + CELL_SIZE // 2
    #             y = row * CELL_SIZE + CELL_SIZE // 2
    #             color = arcade.color.BLUE
    #             arcade.draw_circle_filled(x, y, CELL_SIZE // 3, color)
    #             arcade.draw_text(f"{i+1}", x - CELL_SIZE // 6, y - CELL_SIZE // 6, arcade.color.WHITE, font_size=12)
    #
    #     # Draw bombs
    #     for bomb in self.bombs:
    #         x = bomb.col * CELL_SIZE + CELL_SIZE // 2
    #         y = bomb.row * CELL_SIZE + CELL_SIZE // 2
    #
    #         if bomb.timer == 1:
    #             color = arcade.color.RED
    #             arcade.draw_circle_filled(x, y, CELL_SIZE // 4, color)
    #         elif bomb.timer == 2:
    #             color = arcade.color.ORANGE
    #             arcade.draw_circle_filled(x, y, CELL_SIZE // 4, color)
    #         elif bomb.timer == 0:
    #             pass #explosion are drawn below
    #         else:
    #             color = arcade.color.ASH_GREY
    #             arcade.draw_circle_filled(x, y, CELL_SIZE // 4, color)
    #
    #         #arcade.draw_circle_filled(x, y, CELL_SIZE // 4, color)
    #
    #         if bomb.timer == 0:
    #             arcade.draw_polygon_filled(
    #                      [(x, y - CELL_SIZE // 4), (x + CELL_SIZE // 4, y), (x, y + CELL_SIZE // 4), (x - CELL_SIZE // 4, y)],
    #                      arcade.color.RED)
    #     # for bomb in self.bombs:
    #     #     x = bomb["col"] * CELL_SIZE + CELL_SIZE // 2
    #     #     y = bomb["row"] * CELL_SIZE + CELL_SIZE // 2
    #     #     color = bomb.get("color",
    #     #                      arcade.color.ASH_GREY)  # Default to gray, change to orange and red before explosion
    #     #     arcade.draw_circle_filled(x, y, CELL_SIZE // 4, color)
    #     #
    #     # # Draw red diamonds on explosion positions for this frame only
    #     # for (row, col) in self.explosion_positions:
    #     #     x = col * CELL_SIZE + CELL_SIZE // 2
    #     #     y = row * CELL_SIZE + CELL_SIZE // 2
    #     #     arcade.draw_polygon_filled(
    #     #         [(x, y - CELL_SIZE // 4), (x + CELL_SIZE // 4, y), (x, y + CELL_SIZE // 4), (x - CELL_SIZE // 4, y)],
    #     #         arcade.color.RED
    #     #     )
    #
    #     # Draw scores and lives
    #     for i, (score, lives) in enumerate(zip(self.scores, self.lives)):
    #         arcade.draw_text(f"Agent {i + 1} - Score: {score}, Lives: {lives}",
    #                          10, SCREEN_HEIGHT - 20 * (i + 1), arcade.color.WHITE, font_size=12)


    def create_sprite(self, resource, row, col):
        sprite = arcade.Sprite(resource, 0.3)
        sprite.center_x, sprite.center_y = col * CELL_SIZE + 0.5 * CELL_SIZE, row * CELL_SIZE + 0.5 * CELL_SIZE
        return sprite

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
                    #arcade.draw_rectangle_filled(x, y, CELL_SIZE, CELL_SIZE, arcade.color.RED)
                    self.create_sprite(':resources:images/tiles/boxCrate_double.png', row, col).draw()

                elif self.grid[row][col] == INDESTRUCTIBLE:
                    self.create_sprite(':resources:images/tiles/brickGrey.png', row, col).draw()
                    #arcade.draw_rectangle_filled(x, y, CELL_SIZE, CELL_SIZE, arcade.color.GRAY)
                else:
                    arcade.draw_rectangle_filled(x, y, CELL_SIZE, CELL_SIZE, arcade.color.BLACK)
                    arcade.draw_rectangle_outline(x, y, CELL_SIZE, CELL_SIZE, arcade.color.WHITE)

        for i, (row, col) in enumerate(self.agent_positions):
            if not self.game_over[i]:
                x = col * CELL_SIZE + CELL_SIZE // 2
                y = row * CELL_SIZE + CELL_SIZE // 2
                color = arcade.color.BLUE
                arcade.draw_circle_filled(x, y, CELL_SIZE // 3, color)
                arcade.draw_text(f"{i + 1}", x - CELL_SIZE // 6, y - CELL_SIZE // 6, arcade.color.WHITE, font_size=12)

        # Draw bombs
        for bomb in self.bombs:
            x = bomb.col * CELL_SIZE + CELL_SIZE // 2
            y = bomb.row * CELL_SIZE + CELL_SIZE // 2

            if bomb.timer == 1:
                #color = arcade.color.RED
                #arcade.draw_circle_filled(x, y, CELL_SIZE // 4, color)
                self.create_sprite(':resources:images/tiles/bomb.png', bomb.row, bomb.col).draw()


            elif bomb.timer == 2:
                # color = arcade.color.ORANGE
                # arcade.draw_circle_filled(x, y, CELL_SIZE // 4, color)
                self.create_sprite(':resources:images/tiles/bomb.png', bomb.row, bomb.col).draw()

            elif bomb.timer == 0:
                pass  # Explosion will be drawn below
            else:
                #color = arcade.color.ASH_GREY
                #arcade.draw_circle_filled(x, y, CELL_SIZE // 4, color)
                self.create_sprite(':resources:images/tiles/bomb.png', bomb.row, bomb.col).draw()


            # When the bomb explodes, draw explosion
            if bomb.timer == 0:
                # Draw explosion for the bomb's position
                arcade.draw_polygon_filled(
                    [(x, y - CELL_SIZE // 4), (x + CELL_SIZE // 4, y), (x, y + CELL_SIZE // 4),
                     (x - CELL_SIZE // 4, y)],
                    arcade.color.RED
                )

                # Directions for explosion (right, left, down, up)
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                power = bomb.power  # How far the explosion spreads

                # Draw explosion for neighboring cells based on bomb power
                for dr, dc in directions:
                    for i in range(1, power + 1):  # Explosion spreads based on bomb power
                        r, c = bomb.row + dr * i, bomb.col + dc * i

                        # Ensure the position is within bounds of the grid
                        if 0 <= r < ROWS and 0 <= c < COLS:
                            # Draw explosion at the affected position
                            affected_x = c * CELL_SIZE + CELL_SIZE // 2
                            affected_y = r * CELL_SIZE + CELL_SIZE // 2
                            arcade.draw_polygon_filled(
                                [(affected_x, affected_y - CELL_SIZE // 4),
                                 (affected_x + CELL_SIZE // 4, affected_y),
                                 (affected_x, affected_y + CELL_SIZE // 4),
                                 (affected_x - CELL_SIZE // 4, affected_y)],
                                arcade.color.RED
                            )

                            # If destructible object is hit, destroy it and stop the explosion in that direction
                            if self.grid[r][c] == DESTRUCTIBLE:
                                self.grid[r][c] = EMPTY  # Destroy the object
                                self.scores[bomb.owner] += REWARD_DESTROY_OBJECT
                                break  # Stop explosion in this direction

                            # If indestructible object is hit, stop the explosion in that direction
                            if self.grid[r][c] == INDESTRUCTIBLE:
                                break  # Stop explosion in this direction

        # Draw scores and lives
        for i, (score, lives) in enumerate(zip(self.scores, self.lives)):
            arcade.draw_text(f"Agent {i + 1} - Score: {score}, Lives: {lives}",
                             10, SCREEN_HEIGHT - 20 * (i + 1), arcade.color.WHITE, font_size=12)

        # Draw alpha, gamma, and epsilon values in the top right corner
        alpha_text = f"Alpha: {self.agents[0].alpha}"
        gamma_text = f"Gamma: {self.agents[0].gamma}"
        epsilon_text = f"Epsilon: {self.agents[0].epsilon}"
        generation_text = f"Generation #{self.current_episode + 1}"


        # Draw each text line
        arcade.draw_text(alpha_text,
                         SCREEN_WIDTH - 140 - 10,  # Position text 10 pixels from the right edge
                         SCREEN_HEIGHT - 20,  # 20 pixels from the top edge
                         arcade.color.WHITE, font_size=12)

        arcade.draw_text(gamma_text,
                         SCREEN_WIDTH - 140 - 10,  # Position text 10 pixels from the right edge
                         SCREEN_HEIGHT - 40,  # 40 pixels from the top edge
                         arcade.color.WHITE, font_size=12)

        arcade.draw_text(epsilon_text,
                         SCREEN_WIDTH - 140 - 10,  # Position text 10 pixels from the right edge
                         SCREEN_HEIGHT - 60,  # 60 pixels from the top edge
                         arcade.color.WHITE, font_size=12)

        arcade.draw_text(generation_text,
                         SCREEN_WIDTH - 140 - 10,  # Position text 10 pixels from the right edge
                         SCREEN_HEIGHT - 80,  # 60 pixels from the top edge
                         arcade.color.WHITE, font_size=12)

    def on_update(self, delta_time):
        """Met à jour l'état du jeu."""
        self.time_accumulator += delta_time
        if self.time_accumulator < self.update_interval:
            return
        self.time_accumulator = 0

        for bomb in self.bombs[:]:
            bomb.timer -= 1
            #bomb.timer -= self.update_interval
            if bomb.timer == 0:
                self.explode_bomb(bomb)
            if bomb.timer < 0:
                self.bombs.remove(bomb)

        # for bomb in self.bombs[:]:
        #     bomb["timer"] -= self.update_interval
        #     if bomb["timer"] <= 2:  # Change bomb color to orange just before red
        #         bomb["color"] = arcade.color.ORANGE  # Change to orange
        #     if bomb["timer"] <= 1:  # Change to red just before explosion
        #         bomb["color"] = arcade.color.RED  # Change to red
        #     if bomb["timer"] <= 0:
        #         self.explode_bomb(bomb)
        #         self.bombs.remove(bomb)

        temp = 0
        for i in range(self.num_agents):
            if self.game_over[i]:
                continue
            current_state = self.get_state(i)
            action = self.agents[i].choose_action(current_state)
            temp = action


            reward = self.perform_action(i, action)
            next_state = self.get_state(i)
            self.agents[i].update(current_state, action, reward, next_state)
            if i == 0:
                continue
                #print()
                #print(f"\nAgent {i+1}:\n\tCurrent State: {current_state}\n\tAction: {action} {ACTIONS[action]}\n\tReward: {reward}\n\tNext State: {next_state}")

        # print(f"\n{temp}")
        # print(f"\tState : {self.get_state(0)}\n\tAction : {ACTIONS[action]}")

        # Check if exactly one agent has game_over == False or if all agents are game_over == True
        if self.game_over.count(False) == 1 or all(self.game_over):
            #print(self.agents[0].q_table)
            #print(f"Partie {self.current_episode + 1} terminé. Réinitialisation du jeu.")
            i = 0
            #print(f"Final Scores:")
            for _ in self.agents:
                i += 1
                #self.agents[i-1].history += self.scores[0]
                self.agents[i - 1].history.append(self.scores[0])

                #print(f"\tAgent {i}: {self.scores[i-1]}")
            self.current_episode += 1
            for i, agent in enumerate(self.agents):
                agent.save_q_table(f"agent_{i + 1}_qtable.npy")
            self.setup()


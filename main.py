import arcade
from game import BombermanGame
import matplotlib.pyplot as plt

if __name__ == "__main__":
    game = BombermanGame(num_agents=4)
    game.setup()
    print()
    arcade.run()
    plt.plot(game.agents[0].history)
    plt.show()

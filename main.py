import arcade
from game import BombermanGame


if __name__ == "__main__":
    game = BombermanGame(num_agents=4)
    game.setup()
    print()
    arcade.run()

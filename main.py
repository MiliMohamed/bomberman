import threading
import arcade
import numpy as np
from agent import QLearningAgent, Q_TABLE_LOCATION
from game import BombermanGame
import matplotlib.pyplot as plt


def plot_graph(agent_history):
    plt.ion()  # Interactive mode
    fig, ax = plt.subplots()
    while True:
        ax.clear()
        ax.plot(agent_history)
        ax.set_title("Agent History")
        ax.set_xlabel("Steps")
        ax.set_ylabel("Score")
        plt.pause(0.1)  # Update the plot every 0.1 seconds


if __name__ == "__main__":
    game = BombermanGame(num_agents=2)
    game.setup()

    # Start a thread for plotting
    agent_history = game.agents[0].history
    plot_thread = threading.Thread(target=plot_graph, args=(agent_history,), daemon=True)
    plot_thread.start()

    # Run the game
    arcade.run()

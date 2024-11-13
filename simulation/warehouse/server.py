import mesa
from .model import Maze, Bot, Box, Inside, Outside, Wall
import os

BOT_COLORS = ["#4169E1", "#DC143C", "#228B22", "#FFD700", "#FF4500", "#8A2BE2", "#FF1493", "#00FFFF", "#FF69B4",
              "#FFA500"]

# Read the root path
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


def agent_portrayal(agent):
    if isinstance(agent, Bot):
        return {"Shape": "circle", "Filled": "false", "Color": BOT_COLORS[agent.unique_id - 1], "Layer": 1, "r": 1.0,
                "text": f"{agent.unique_id}", "text_color": "black"}
    elif isinstance(agent, Box):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "#2F4F4F",
                "Color": "rgba(112, 66, 20, 0.5)", "text": "📦"}
    elif isinstance(agent, Inside):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 1, "h": 1, "text_color": "#2F4F4F",
                "Color": "rgba(0, 255, 0, 0.3)", "text": "🟩"}
    elif isinstance(agent, Outside):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 1, "h": 1, "text_color": "#2F4F4F",
                "Color": "rgba(255, 0, 0, 0.3)", "text": "🟥"}
    elif isinstance(agent, Wall):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 1, "h": 1, "text_color": "#2F4F4F",
                "Color": "rgba(0, 0, 0, 1)", "text": "🧱"}


grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 115, 90, 800, 800)



def model_params():
    params = {}

    return params


server = mesa.visualization.ModularServer(
    Maze, [grid],
    "Simulacion", model_params(), 6969
)

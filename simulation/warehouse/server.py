import mesa
import os
from .model import Maze, LGVManager, LGV, Rack, unusableRack, Inside, unusableInside, Outside, unusableOutside, Wall
from mesa.visualization.modules import ChartModule


BOT_COLORS = ["#4169E1", "#DC143C", "#228B22", "#FFD700", "#FF4500", "#8A2BE2", "#FF1493", "#00FFFF", "#FF69B4",
              "#FFA500"]

# Read the root path
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


def agent_portrayal(agent):
    if isinstance(agent, LGV):
        return {"Shape": "circle", "Filled": "false", "Color": BOT_COLORS[agent.unique_id - 1], "Layer": 1, "r": 1.0,
                "text": f"{agent.unique_id}", "text_color": "black"}
    elif isinstance(agent, Rack):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "#2F4F4F",
                "Color": "rgba(112, 66, 20, 0.5)", "text": "📦"}
    elif isinstance(agent, unusableRack):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "#2F4F4F",
                "Color": "rgba(112, 66, 20, 0.5)", "text": "🚫"}
    elif isinstance(agent, Inside):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 1, "h": 1, "text_color": "#2F4F4F",
                "Color": "rgba(0, 255, 0, 0.3)", "text": "🟩"}
    elif isinstance(agent, unusableInside):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 1, "h": 1, "text_color": "#2F4F4F",
                "Color": "rgba(0, 255, 0, 0.3)", "text": "🚫"}
    elif isinstance(agent, Outside):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 1, "h": 1, "text_color": "#2F4F4F",
                "Color": "rgba(255, 0, 0, 0.3)", "text": "🟥"}
    elif isinstance(agent, unusableOutside):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 1, "h": 1, "text_color": "#2F4F4F",
                "Color": "rgba(255, 0, 0, 0.3)", "text": "🚫"}
    elif isinstance(agent, Wall):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 1, "h": 1, "text_color": "#2F4F4F",
                "Color": "rgba(0, 0, 0, 1)", "text": "🧱"}



grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 115, 90, 900, 900)



def model_params():
    params = {}
    
    params["lgvs"] = mesa.visualization.Slider(
        name="lgvs",
        min_value=3,
        max_value=5,
        value=3,
        step=1,
        description="Number of LGVs",
    )
    
    params["time"] = mesa.visualization.Slider(
        name="time",
        min_value=1,
        max_value=100,
        value=1,
        step=1,
        description="Simulation time",
    )

    return params


battery_chart = ChartModule(
    [{"Label": "Average_Battery", "Color": "Blue"}],
    data_collector_name="datacollector"
)



server = mesa.visualization.ModularServer(
    Maze, [grid, battery_chart],
    "Simulacion", model_params(), 6969
)

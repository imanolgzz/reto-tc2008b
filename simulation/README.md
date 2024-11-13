# Warehouse Simulation


###
###
### MODIFY README
###
###





## Description
This is a simple maze game to capture the flag(s) where there are bots that are trying to reach the end of the maze. The bots are controlled by a simple reinforcement learning algorithm like Q-learning. The maze is a 2D grid where the bots can move up, down, left, or right. The bots can only move to a cell that is not a box. The bots can only see the cells that are adjacent to them.

## Installation
1. Clone the repository
2. Install the required packages
```bash
pip install -r requirements.txt
```

## Usage
1. Run the game
```bash
python run.py
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details


## Directory Structure
```bash
7-Maze_RL/
├── README.md
├── requirements.txt
├── run.py
└── 7-Maze_RL/
    ├── __init__.py
    ├── agent.py
    ├── model.py
    ├── server.py
    ├── maze_designer.py
    └── mazes/
        ├── maze1.txt
        ├── maze2.txt
        ├── maze3.txt
        ├── maze4.txt
        └── ...
```

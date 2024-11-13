import os

from mesa.model import Model
from .agent import Box, Bot, Inside, Outside, Wall

from mesa.space import SingleGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector



class Maze(Model):
    def __init__(self):
        super().__init__()
        
        desc_file = "maze.txt"        
        root_path = os.path.dirname(os.path.abspath(__file__))
        desc = self.from_txt_to_desc(root_path + "/" + desc_file)
        
        # Get the dimensions of the environment
        M, N = len(desc), len(desc[0])
        
        print(f"Creating a {M}x{N} maze")

        # Get the number of bots in the environment from the description
        num_bots = 0
        for i in range(M):
            for j in range(N):
                if desc[i][j].isdigit():
                    num_bots += 1
        self.num_bots = num_bots
        self.bots = {}

        # Create the grid and schedule
        # how to create a grid: https://mesa.readthedocs.io/en/stable/tutorials/intro_tutorial.html
        self.grid = SingleGrid(N, M, False)
        self.schedule = SimultaneousActivation(self)

        # Place agents in the environment
        self.place_agents(desc)

        self.states = {}
        self.rewards = {}
        for state, cell in enumerate(self.grid.coord_iter()):
            a, pos = cell

            # Define states for the environment
            self.states[pos] = state

            # Define rewards for the environment
            if isinstance(a, Box):
                self.rewards[state] = -1
            else:
                self.rewards[state] = 0.1

    def step(self):
        # Train the agents in the environment
        for bot_id, bot in self.bots.items():
            # print(f"Training bot {bot_id} {bot.unique_id}")
            if self.__getattribute__(f"train_bot{bot_id}"):
                bot.train()
                self.__setattr__(f"train_bot{bot_id}", False)

        self.schedule.step()

        self.running = not any([a.done for a in self.schedule.agents])

    def place_agents(self, desc: list):
        #M, N = self.grid.height, self.grid.width
        
        #print(f"Desc: {desc}")
        #print(f"Desc height: {len(desc)}")
        #print(f"Desc width: {len(desc[0])}")
        
        #print(f"Grid height: {self.grid.height}")
        #print(f"Grid width: {self.grid.width}")
        
        for pos in self.grid.coord_iter():
            _, (x, y) = pos
            
            #print(f"Placing agent at {x}, {y}")
            
            #print(f"Desc: {desc}")
            #print(f"Desc height: {self.grid.height}")
            #print(f"Desc width: {self.grid.width}")
            
            if desc[y][x] == 'S':
                box = Box(int(f"1000{x}{y}"), self)
                self.grid.place_agent(box, (x, y))
            elif desc[y][x] == 'O':
                outside = Outside(int(f"10{x}{y}"), self)
                self.grid.place_agent(outside, (x, y))
            elif desc[y][x] == 'I':
                inside = Inside(int(f"10{x}{y}"), self)
                self.grid.place_agent(inside, (x, y))
            elif desc[y][x] == 'M':
                wall = Wall(int(f"10{x}{y}"), self)
                self.grid.place_agent(wall, (x, y))
            else:
                try:
                    bot_num = int(desc[y][x])
                    bot = Bot(int(f"{bot_num}"), self)
                    self.grid.place_agent(bot, (x, y))
                    self.schedule.add(bot)
                    self.bots[bot_num] = bot

                except ValueError:
                    pass

    @staticmethod
    def from_txt_to_desc(file_path):
        try:
            with open(file_path, 'r') as file:
                desc = [line.strip() for line in file.readlines()][::-1]
            return desc
        except Exception as e:
            print(f"Error reading the file: {e}")
            return None

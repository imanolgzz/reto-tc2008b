import os

from mesa.model import Model
from .agent import LGVManager, LGV, Rack, unusableRack, Inside, unusableInside, Outside, unusableOutside, Wall

from mesa.space import SingleGrid
from mesa.time import SimultaneousActivation


class Maze(Model):
    def __init__(self, **kwargs):
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
        self.grid = SingleGrid(N, M, False)
        self.schedule = SimultaneousActivation(self)

        # Place agents in the environment
        self.place_agents(desc)

    def step(self):
        self.schedule.step()

        self.running = not any([a.done for a in self.schedule.agents])


    def place_agents(self, desc: list):
        for pos in self.grid.coord_iter():
            _, (x, y) = pos
            char = desc[y][x]
            
            if char == 'S':
                # if rack is blocked by racks in all 4 directions, it is unusable
                if ((desc[y-1][x] in {'S', 'M'}) and (desc[y+1][x] in {'S', 'M'}) and (desc[y][x-1] in {'S', 'M'}) and (desc[y][x+1] in {'S', 'M'})):
                    unusablerack = unusableRack(int(f"1000{x}{y}"), self)
                    self.grid.place_agent(unusablerack, (x, y))
                else:
                    rack = Rack(int(f"1000{x}{y}"), self)
                    self.grid.place_agent(rack, (x, y))
            elif desc[y][x] == 'O':
                outside = Outside(int(f"10{x}{y}"), self)
                self.grid.place_agent(outside, (x, y))
            elif desc[y][x] == 'U':
                unusableoutside = unusableOutside(int(f"10{x}{y}"), self)
                self.grid.place_agent(unusableoutside, (x, y))
            elif desc[y][x] == 'I':
                inside = Inside(int(f"10{x}{y}"), self)
                self.grid.place_agent(inside, (x, y))
            elif desc[y][x] == 'J':
                unusableinside = unusableInside(int(f"10{x}{y}"), self)
                self.grid.place_agent(unusableinside, (x, y))
            elif desc[y][x] == 'M':
                wall = Wall(int(f"10{x}{y}"), self)
                self.grid.place_agent(wall, (x, y))
            else:
                try:
                    bot_num = int(desc[y][x])
                    bot = LGV(int(f"{bot_num}"), self)
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

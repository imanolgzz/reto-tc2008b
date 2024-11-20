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

        # Get the number of bots in the environment from model_params
        self.num_bots = kwargs.get('lgvs', 0)

        # Create the grid and schedule
        self.grid = SingleGrid(N, M, False)
        self.schedule = SimultaneousActivation(self)

        # Place agents in the environment
        self.place_agents(desc)

        # Add LGVManager agent
        # manager = LGVManager(0, self)
        # self.grid.place_agent(manager, (0, 0))
        # self.schedule.add(manager)

    def step(self):
        self.schedule.step()

        self.running = not any([a.done for a in self.schedule.agents])


    def place_agents(self, desc: list):
        # poner todos los obstaculos y racks del mapa
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
                pass

        # poner los bots de manera random
        for i in range(self.num_bots):
            x, y = self.random.choice(list(self.grid.empties))
            bot = LGV(int(f"{i}"), self)
            self.grid.place_agent(bot, (x, y))
            self.schedule.add(bot)

    @staticmethod
    def from_txt_to_desc(file_path):
        try:
            with open(file_path, 'r') as file:
                desc = [line.strip() for line in file.readlines()][::-1]
            return desc
        except Exception as e:
            print(f"Error reading the file: {e}")
            return None

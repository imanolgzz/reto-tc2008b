import os

from mesa.model import Model
from .agent import LGVManager, LGV, Rack, unusableRack, Inside, unusableInside, Outside, unusableOutside, Wall

from mesa.space import SingleGrid
from mesa.time import SimultaneousActivation

from mesa.datacollection import DataCollector


class Maze(Model):
    def __init__(self, **kwargs):
        super().__init__()
        
        desc_file = "maze.txt"        
        root_path = os.path.dirname(os.path.abspath(__file__))
        desc = self.from_txt_to_desc(root_path + "/" + desc_file)
        with open(root_path + "/outputModel.txt", 'w') as output_file:
            for line in desc:
                output_file.write(f"{line}\n")
        
        # Get the dimensions of the environment
        M, N = len(desc), len(desc[0])
        
        print(f"Creating a {M}x{N} maze")

        # Get the number of bots in the environment from model_params
        self.num_bots = kwargs.get('lgvs', 0)

        time = kwargs.get('time', 12) # tiempo en minutos
        
        self.racksid = 1

        # Create the grid and schedule
        self.grid = SingleGrid(N, M, False)
        self.schedule = SimultaneousActivation(self)

        # Add LGVManager agent
        manager = LGVManager(6, self, time)
        self.schedule.add(manager)

        # Place agents in the environment
        self.place_agents(desc, manager)
        
        # self.datacollector = DataCollector(
        #     model_reporters={
        #         "Average_Battery": lambda model: self.get_average_battery(manager),
        #     },
        #     agent_reporters={}
        # )
        
        # self.datacollector = DataCollector(
        #     model_reporters={
        #         **{
        #             f"Bot_{bot_id}": lambda model, bot_id=bot_id: manager.get_battery_levels().get(bot_id, 0)
        #             for bot_id in range(self.num_bots)
        #         }
        #     },
        #     agent_reporters={}
        # )


        



    def step(self):
        #self.datacollector.collect(self)
        self.schedule.step()
        self.running = not all(a.done for a in self.schedule.agents)
        
    # def get_average_battery(self, manager: LGVManager = None):
    #     if manager:
    #         battery_values = list(manager.get_battery_levels().values())
    #         return sum(battery_values) / len(battery_values) if battery_values else 0
    #     return 0
    
    def get_battery_levels(self, manager: LGVManager = None):
        if manager:
            return manager.get_battery_levels().values() if manager.get_battery_levels() else {}
        return {}

    def place_agents(self, desc: list, manager: LGVManager):
        """
        Coloca los agentes en el grid basado en la descripción del laberinto.
        Ajusta el eje Y para que el archivo se grafique tal como aparece.
        """
        salidas = 0
        chargers = 0
        # Recorre las filas (desc), ajustando el eje Y para que sea invertido
        for y, row in enumerate(desc):
            for x, char in enumerate(row):
                # Calcula la posición invertida en el eje Y
                inverted_y = len(desc) - y - 1

                if char == 'S':
                    if self.is_blocked(desc, x, y):
                        unusablerack = unusableRack(int(f"1000{x}{y}"), self)
                        self.grid.place_agent(unusablerack, (x, inverted_y))
                    else:
                        rack = Rack(int(f"1000{x}{y}"), self)
                        self.grid.place_agent(rack, (x, inverted_y))
                        manager.add_rack(self.racksid, (x, inverted_y))
                        self.racksid += 1
                elif char == 'O':
                    outside = Outside(int(f"10{x}{y}"), self)
                    self.grid.place_agent(outside, (x, inverted_y))
                    manager.cords[f"salida{salidas}"] = (x, inverted_y-1)
                    salidas += 1
                elif char == 'U':
                    unusableoutside = unusableOutside(int(f"10{x}{y}"), self)
                    self.grid.place_agent(unusableoutside, (x, inverted_y))
                elif char == 'I':
                    inside = Inside(int(f"10{x}{y}"), self)
                    self.grid.place_agent(inside, (x, inverted_y))
                    manager.cords["entrada0"] = (x, inverted_y+1)
                    manager.cords["entrada1"] = (x+1, inverted_y)
                    manager.cords["entrada2"] = (x, inverted_y-1)
                elif char == 'J':
                    unusableinside = unusableInside(int(f"10{x}{y}"), self)
                    self.grid.place_agent(unusableinside, (x, inverted_y))
                elif char == 'M':
                    wall = Wall(int(f"10{x}{y}"), self)
                    self.grid.place_agent(wall, (x, inverted_y))
                    # poner los bots de manera random
                elif char == 'C':
                    manager.cords[f"cargador{chargers}"] = (x, inverted_y-1)
                    chargers += 1
                    
        for i in range(self.num_bots):
            x, y = self.random.choice(list(self.grid.empties))
            bot = LGV(int(f"{i}"), self, (x, y))
            manager.add_bot(bot)
            self.grid.place_agent(bot, (x, y))

    @staticmethod
    def is_blocked(desc, x, y):
        """
        Verifica si un rack está bloqueado en las 4 direcciones.
        """
        try:
            return (
                desc[y - 1][x] in {'S', 'M'} and
                desc[y + 1][x] in {'S', 'M'} and
                desc[y][x - 1] in {'S', 'M'} and
                desc[y][x + 1] in {'S', 'M'}
            )
        except IndexError:
            return False

    @staticmethod
    def from_txt_to_desc(file_path):
        try:
            with open(file_path, 'r') as file:
                desc = [line.strip() for line in file.readlines()]
            return desc
        except Exception as e:
            print(f"Error reading the file: {e}")
            return None

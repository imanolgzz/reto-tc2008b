from mesa.agent import Agent
import queue
import os

class LGVManager(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.bots = {}
        self.cords = []
        self.tasks = queue.Queue()
        self.current_step = 0

    def add_bot(self, id, pos):
        self.bots[id] = pos


    def assign_tasks(self, task):
        self.tasks.put(task)

    def step(self):
        if self.current_step % 120 == 0:
            # add entrada-salida
            for i in range(10):
                self.assign_tasks({"task": "entrada-salida"})

            for i in range(20):
                self.assign_tasks({"task": "entrada-rack"})

            for i in range(25):
                self.assign_tasks({"task": "rack-rack"})

        # asignar tasks a los bots
        if not self.tasks.empty(): # verificar que haya tasks para asignar
            available_bots = []
            for bot in self.bots:
                if bot.hasTask == False:
                    available_bots.append(bot)

            # checar cuantos bots hay disponibles
            if len(available_bots) == 0:
                # no hay bots disponibles
                return
            elif len(available_bots) > 1:
                # mas de un bot disponible, hay que seleccionr el más adecuado
                for i in range(len(available_bots)):
                    if self.tasks.queue[0]["task"] == "entrada-salida" :
                        # seleccionar el bot más cercano a la entrada
                        pass
                    elif self.tasks.queue[0]["task"] == "entrada-rack":
                        # seleccionar el bot más cercano a la entrada

                        # buscar el rack más cercano con disponibilidad de storage
                        pass
                    else:
                        # seleccionar el bot más cercano a un rack con palletes
                        pass
            else:
                # solo hay un bot disponible
                pass


        

            


        self.current_step += 1
        

        
        
class LGV(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.hasTask = False
        self.hasPallete = False
        self.pos = pos
        self.path = []
        self.target = queue.Queue()

    
    
    
    
    
    
class Rack(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class unusableRack(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Inside(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class unusableInside(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class Outside(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
class unusableOutside(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)        
        
class Wall(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
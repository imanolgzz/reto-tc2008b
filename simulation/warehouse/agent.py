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

        # checar si hay bots sin tasks
        available_bots = []
        for bot in self.bots:
            if bot.hasTask == False:
                available_bots.append(bot)

        # asignar tasks a los bots en caso de que haya almenos uno desocupado
        if not self.tasks.empty() and len(available_bots) > 0: # verificar que haya tasks para asignar
            # checar cuantos bots hay disponibles
            if len(available_bots) > 1:
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
        # bots ocupados
        else:
            # checar las posiciones que tendrían los bots el siguiente step
            next_posArr = [] # [(x,y), (x,y)]
            for bot in self.bots:
                next_pos = bot.getNextPos()
                if next_pos:
                    next_posArr.append(next_pos)
            # comparar todas las next pos para verificar que no haya colisiones (solo funciona si las coordenadas son tuplas)
            if len(set(next_posArr)) != len(next_posArr):
                # hay colisiones
                """
                ejemplo reconocer tuplas repetidas y obtener indices de repetidos:
                
                coordinates = [(1, 2), (3, 4), (1, 2)]

                # Crear un diccionario para rastrear índices de cada coordenada
                from collections import defaultdict

                indices = defaultdict(list)

                # Rellenar el diccionario con los índices de cada coordenada
                for index, coord in enumerate(coordinates):
                    indices[coord].append(index)

                # Filtrar las coordenadas que tienen más de un índice (repetidas)
                duplicates = {coord: idx_list for coord, idx_list in indices.items() if len(idx_list) > 1} # boleana
                
                """
                pass
            else:
                # bots hacen su step normal
                for bot in self.bots:
                    bot.step()

            # si alguno va a chocar, posponer el step de uno y que el otro siga

            # else 
            pass



        

            


        self.current_step += 1
        

        
        
class LGV(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.hasTask = False
        self.hasPallete = False
        self.pos = pos
        self.path = queue.Queue() # path = [(x,y), (x,y)] -> cada step es cuadro
        self.target = queue.Queue() # target = [(x,y), (x,y)]
        self.map = self.read_map()

    def astar(self, start, end):  # pos, target
        pass

    def getNextPos(self):
        return self.path.queue[0] if not self.path.empty() else None

    def step(self):
        if self.hasTask:
            # si tiene una tarea asignada, moverse a la siguiente posición
            if not self.path.empty():
                self.pos = self.path.get()
                if self.pos == self.target:
                    self.hasTask = False
                    self.hasPallete = False
        else:
            # si no tiene una tarea asignada, esperar
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

    def read_map(self):
        desc_file = "maze.txt"        
        root_path = os.path.dirname(os.path.abspath(__file__))
        desc = self.from_txt_to_desc(root_path + "/" + desc_file)
        return desc
    

    
    
    
    
    
    
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
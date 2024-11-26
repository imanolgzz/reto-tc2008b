from mesa.agent import Agent
from collections import defaultdict
import queue
import heapq
import os

class LGVManager(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.bots = []
        self.cords = []
        self.tasks = queue.Queue()
        self.current_step = 0
        self.racks = []

    def add_bot(self, bot):
        self.bots.append(bot)
        
    def add_rack(self, id, pos):
        self.racks.append((id, pos, 0))

    def assign_tasks(self, task):
        self.tasks.put(task)
        
    
    def calc_distance(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def closest_rack(self, bot_id):
        bot_pos = self.bots.get(bot_id)
        eligible_racks = [rack for rack in self.racks if rack[2] < 3]
        
        if not eligible_racks:
            return None
        
        distances = [
            {
                "rack": rack,
                "distance": self.calc_distance(bot_pos, rack[1])
            }
            for rack in eligible_racks
        ]
        
        closest_rack = min(distances, key=lambda d: d["distance"])
        return closest_rack["rack"]

    def check_collision(self, next_pos):
        indices = defaultdict(list)

        # Rellenar el diccionario con los índices de cada coordenada
        for index, coord in enumerate(next_pos):
            indices[coord].append(index)

        # Filtrar las coordenadas que tienen más de un índice (repetidas)
        duplicates = {coord: idx_list for coord, idx_list in indices.items() if len(idx_list) > 1} # boleana

        for coord, idx_list in duplicates.items():
            print(f"Coordenada {coord} repetida en índices {idx_list}")
        
        # Seleccionar coordenadas únicas y sus índices
        selected_coords = []
        selected_indices = []
        seen_coords = set()

        for index, coord in enumerate(next_pos):
            if coord not in seen_coords:
                selected_coords.append(coord)
                selected_indices.append(index)
                seen_coords.add(coord)

        return selected_coords, selected_indices

    def eucladian_distance(self, bots, dest):
        bot_min = None
        min_distance = float('inf')
        for i, bot in enumerate(bots):
            distance = ((bot[0] - dest[0])**2 + (bot[1] - dest[1])**2)**0.5
            if distance < min_distance:
                min_distance = distance
                bot_min = i
        return bot_min

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
                        # todo seleccionar el bot más cercano a la entrada
                        best = self.eucladian_distance(available_bots, self.cords["entrada"])
                        bot = available_bots[best]
                        bot.asign_task(target = [self.cords["entrada"], self.cords["salida"]])
                    elif self.tasks.queue[0]["task"] == "entrada-rack":
                        # todo seleccionar el bot más cercano a la entrada
                        best = self.eucladian_distance(available_bots, self.cords["entrada"])
                        bot = available_bots[best]
                        # todo nico buscar el rack más cercano con disponibilidad de storage
                        pass
                    else:
                        # todo seleccionar el bot más cercano a un rack con palletes
                        pass
            else:
                # todo solo hay un bot disponible, asignarle la tarea
                bot = available_bots[0]
                if self.tasks.queue[0]["task"] == "entrada-salida" :
                    bot.asign_task(target = [self.cords["entrada"], self.cords["salida"]])
                elif self.tasks.queue[0]["task"] == "entrada-rack":
                    # todo nico buscar el rack más cercano con disponibilidad de storage
                    pass
                else:
                    # todo seleccionar el bot más cercano a un rack con palletes
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
                # coords regresa las coordenadas que si pasan el filtro, indexes regresa el indice de los bots que si pueden hacer step
                coords, indexes = self.check_collision(next_posArr) # indexes ya dice el indice de los bots que hacen el step dentro de 
                for i in range(len(self.bots)):
                    if i in indexes:
                        self.bots[i].step()
            else:
                # bots hacen su step normal
                for bot in self.bots:
                    bot.step()

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

    def astar(self, start, end):
        # Convertir el mapa actual en una representación binaria
        grid = [[1 if char in {'M', 'S', 'U', 'J'} else 0 for char in row] for row in self.map]

        # Implementar A*
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, end)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return queue.Queue(path)

            neighbors = [(current[0] + dx, current[1] + dy) for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]]
            for neighbor in neighbors:
                if (0 <= neighbor[0] < len(grid) and 0 <= neighbor[1] < len(grid[0]) and grid[neighbor[0]][neighbor[1]] == 0):
                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return queue.Queue()  # Si no hay camino


    def getNextPos(self):
        return self.path.queue[0] if not self.path.empty() else None

    def asign_task(self, target):
        for cord in target:
            self.target.append(cord)
        self.path = self.astar(self.pos, self.target[0]) # el primer target
        self.hasTask = True

    def step(self):
        if self.hasTask:
            # si tiene una tarea asignada, moverse a la siguiente posición
            if not self.path.empty(): # aun le quedan pasos por dar
                self.pos = self.path.get()
                if self.pos == self.target and len(self.target) == 1: # ya es su ultimo target
                    self.hasTask = False
                    self.hasPallete = False
                elif self.pos == self.target and len(self.target) > 1: # aun tiene otro target
                    self.target.popleft()
                    self.path = self.astar(self.pos, self.target[0])
                    self.hasPallete = True # en el primer target siempre recoge un pallete

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
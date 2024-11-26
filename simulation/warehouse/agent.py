from mesa.agent import Agent
from collections import defaultdict, deque
import queue
import heapq
import os

class LGVManager(Agent):
    def __init__(self, unique_id, model, time):
        super().__init__(unique_id, model)
        self.bots = []
        self.cords = {}
        self.tasks = queue.Queue()
        self.current_step = 0
        self.racks = []
        self.time = time*60
        self.done = False
        #print(f"[DEBUG] LGVManager inicializado con tiempo límite: {self.time} segundos")

    def add_bot(self, bot):
        self.bots.append(bot)
        #print(f"[DEBUG] Bot añadido: ID={bot.unique_id}, posición inicial={bot.pos}")
        
    def add_rack(self, id, pos):
        self.racks.append((id, pos, 0))
        #print(f"[DEBUG] Rack añadido: ID={id}, posición={pos}")

    def assign_tasks(self, task):
        self.tasks.put(task)
        #print(f"[DEBUG] Tarea asignada: {task}")
    
    def calc_distance(pos1, pos2):
        distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        print(f"[DEBUG] Calculando distancia entre {pos1} y {pos2}: {distance}")
        return distance
    
    def closest_rack(self, bot_id):
        print(f"[DEBUG] Buscando rack más cercano para bot ID={bot_id}")
        bot_pos = self.bots.get(bot_id)
        eligible_racks = [rack for rack in self.racks if rack[2] < 3]
        print(f"[DEBUG] Racks elegibles: {eligible_racks}")
        
        if not eligible_racks:
            print("[DEBUG] No hay racks elegibles disponibles")
            return None
        
        distances = [
            {
                "rack": rack,
                "distance": self.calc_distance(bot_pos, rack[1])
            }
            for rack in eligible_racks
        ]
        
        closest_rack = min(distances, key=lambda d: d["distance"])
        print(f"[DEBUG] Rack más cercano encontrado: {closest_rack}")
        return closest_rack["rack"]
    
    def find_nearest_bot_to_pallet(self, available_bots):
        print(f"[DEBUG] Buscando bot más cercano a un rack con pallets disponibles")
        racks_with_pallets = [rack for rack in self.racks if rack[2] > 0]
        print(f"[DEBUG] Racks con pallets: {racks_with_pallets}")

        if not racks_with_pallets:
            print("[DEBUG] No hay racks con pallets disponibles")
            return None

        closest_bot = None
        closest_rack = None
        min_distance = float('inf')

        for bot in available_bots:
            bot_pos = bot.get_position()
            for rack in racks_with_pallets:
                distance = self.calc_distance(bot_pos, rack[1])
                if distance < min_distance:
                    min_distance = distance
                    closest_bot = bot
                    closest_rack = rack

        print(f"[DEBUG] Bot más cercano: {closest_bot}, Rack más cercano: {closest_rack}")
        return closest_bot, closest_rack

    def check_collision(self, next_pos):
        print(f"[DEBUG] Comprobando colisiones para posiciones: {next_pos}")
        indices = defaultdict(list)

        for index, coord in enumerate(next_pos):
            indices[coord].append(index)

        duplicates = {coord: idx_list for coord, idx_list in indices.items() if len(idx_list) > 1}
        if duplicates:
            print(f"[DEBUG] Colisiones detectadas: {duplicates}")
        
        selected_coords = []
        selected_indices = []
        seen_coords = set()

        for index, coord in enumerate(next_pos):
            if coord not in seen_coords:
                selected_coords.append(coord)
                selected_indices.append(index)
                seen_coords.add(coord)

        print(f"[DEBUG] Coordenadas seleccionadas: {selected_coords}, Índices: {selected_indices}")
        return selected_coords, selected_indices

    def eucladian_distance(self, bots, dest):
        print(f"[DEBUG] Calculando distancia euclidiana a destino {dest}")
        bot_min_index = None
        min_distance = float('inf')
        for i, bot in enumerate(bots):
            bot_pos = bot.pos
            distance = ((bot_pos[0] - dest[0])**2 + (bot_pos[1] - dest[1])**2)**0.5
            print(f"[DEBUG] Bot ID={bot.unique_id}, Posición={bot_pos}, Distancia={distance}")
            if distance < min_distance:
                min_distance = distance
                bot_min_index = i
        print(f"[DEBUG] Bot más cercano: índice={bot_min_index}")
        return bot_min_index

    def step(self):
        print(f"\n[STEP {self.current_step}] Iniciando paso del LGVManager")
        if self.current_step >= self.time: # terminar simulación
            self.done = True
            print("[DEBUG] Tiempo límite alcanzado. Finalizando simulación.")
            return

        if self.current_step % 120 == 0:
            print("[DEBUG] Generando nuevas tareas...")
            # add entrada-salida
            for i in range(10):
                self.assign_tasks({"task": "entrada-salida"})

            for i in range(20):
                self.assign_tasks({"task": "entrada-rack"})

            for i in range(25):
                self.assign_tasks({"task": "rack-rack"})

        print(f"[DEBUG] Total de tareas en cola: {self.tasks.qsize()}")

        # checar si hay bots sin tasks
        available_bots = []
        for bot in self.bots:
            if bot.hasTask == False:
                available_bots.append(bot)

        print(f"[DEBUG] Bots disponibles: {[bot.unique_id for bot in available_bots]}")

        # Asignar tareas a los bots disponibles
        if not self.tasks.empty() and available_bots:
            print(f"[DEBUG] Asignando tareas a {len(available_bots)} bots disponibles...")
            if len(available_bots) > 1:  # Más de un bot disponible
                for i in range(len(available_bots)):
                    current_task = self.tasks.queue[0]  # Consultar la tarea en la parte frontal de la cola
                    print(f"[DEBUG] Evaluando tarea: {current_task}")
                    if current_task["task"] == "entrada-salida":
                        best = self.eucladian_distance(available_bots, self.cords["entrada"])
                        bot = available_bots[best]
                        bot.asign_task(target=[self.cords["entrada"], self.cords["salida"]])
                        print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-salida")
                        available_bots.remove(bot)
                    elif current_task["task"] == "entrada-rack":
                        best = self.eucladian_distance(available_bots, self.cords["entrada"])
                        bot = available_bots[best]
                        rack = self.closest_rack(bot.unique_id)
                        if rack:
                            print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-rack con rack ID={rack[0]}")
                            available_bots.remove(bot)
                        else:
                            print("[DEBUG] No hay racks disponibles para entrada-rack.")
                    else:
                        closest_bot, closest_rack = self.find_nearest_bot_to_pallet(available_bots)
                        if closest_bot and closest_rack:
                            print(f"[DEBUG] Bot {closest_bot.unique_id} asignado a rack-rack con rack ID={closest_rack[0]}")
                            available_bots.remove(bot)

            else:  # Solo un bot disponible
                bot = available_bots[0]
                current_task = self.tasks.queue[0]
                print(f"[DEBUG] Evaluando tarea: {current_task}")
                if current_task["task"] == "entrada-salida":
                    bot.asign_task(target=[self.cords["entrada"], self.cords["salida"]])
                    print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-salida")
                    available_bots.remove(bot)
                elif current_task["task"] == "entrada-rack":
                    rack = self.closest_rack(bot.unique_id)
                    if rack:
                        print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-rack con rack ID={rack[0]}")
                        available_bots.remove(bot)
                    else:
                        print("[DEBUG] No hay racks disponibles para entrada-rack.")
                else:
                    closest_bot, closest_rack = self.find_nearest_bot_to_pallet(bot)
                    if closest_bot and closest_rack:
                        print(f"[DEBUG] Bot {closest_bot.unique_id} asignado a rack-rack con rack ID={closest_rack[0]}")
                        available_bots.remove(bot)
        # Manejar bots ocupados o en movimiento
        else:
            print("[DEBUG] Verificando próximas posiciones de los bots...")
            next_posArr = []  # [(x, y), (x, y)]
            for bot in self.bots:
                next_pos = bot.getNextPos()
                print(f"[DEBUG] Bot {bot.unique_id} próxima posición: {next_pos}")
                if next_pos:
                    next_posArr.append(next_pos)
            print(f"[DEBUG] Próximas posiciones: {next_posArr}")

            # Comprobar colisiones
            if len(set(next_posArr)) != len(next_posArr):
                print("[DEBUG] Colisiones detectadas. Resolviendo...")
                coords, indexes = self.check_collision(next_posArr)
                for i in indexes:
                    print(f"[DEBUG] Bot {self.bots[i].unique_id} avanzando a {coords[i]}")
                    self.bots[i].step()
            else:
                for bot in self.bots:
                    bot.step()
                    print(f"[DEBUG] Bot {bot.unique_id} avanzó a {bot.pos}")

        self.current_step += 1
        print(f"[STEP {self.current_step}] Finalizando paso del LGVManager\n")


        

        
        
class LGV(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.hasTask = False
        self.hasPallete = False
        self.pos = pos
        self.path = queue.Queue() # path = [(x,y), (x,y)] -> cada step es cuadro
        self.target = [] # target = [(x,y), (x,y)]
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
                #print(f"[DEBUG] Camino encontrado: {path}")
                queue_path = queue.Queue()
                for step in path:
                    queue_path.put(step)  # Rellena correctamente la cola
                return queue_path

            neighbors = [(current[0] + dx, current[1] + dy) for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]]
            for neighbor in neighbors:
                if (0 <= neighbor[0] < len(grid) and 0 <= neighbor[1] < len(grid[0]) and grid[neighbor[0]][neighbor[1]] == 0):
                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        print("[DEBUG] No se encontró camino")
        return queue.Queue()  # Si no hay camino


    def getNextPos(self):
        return self.path.queue[0] if not self.path.empty() else None

    def asign_task(self, target):
        for cord in target:
            self.target.append(cord)
        print(f"[BOT] Bot ID={self.unique_id} asignado a tarea con target {self.target}")
        self.path = self.astar(self.pos, self.target[0]) # usa el primer target 
        print(f"[BOT] Bot ID={self.unique_id} con path {list(self.path.queue)}")
        self.hasTask = True

    def step(self):
        if self.hasTask:
            print(f"[BOT] Step del bot ID={self.unique_id} con tarea asignada y posición {self.pos}")

            # si tiene una tarea asignada, moverse a la siguiente posición
            if not self.path.empty(): # aun le quedan pasos por dar
                self.pos = self.path.get()
                print(f"[BOT] Bot ID={self.unique_id} avanzando a {self.pos}")
                if self.pos == self.target[0] and len(self.target) > 1: # aun tiene otro target
                    self.target.pop(0)
                    self.path = self.astar(self.pos, self.target[0])
                    self.hasPallete = True # en el primer target siempre recoge un pallete
                elif self.pos == self.target[0] and len(self.target) == 1: # ya es su ultimo target
                    self.hasTask = False
                    self.hasPallete = False
                    self.target = []

        else:
            print(f"[BOT] Step del bot ID={self.unique_id} sin tarea")
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
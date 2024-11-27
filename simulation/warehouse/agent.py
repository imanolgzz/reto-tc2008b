from mesa.agent import Agent
from collections import defaultdict, deque
import queue
import heapq
import os
import random
import json

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

    def generate_json(self):
        steps_data = []
        for step in range(self.current_step + 1):
            agents_data = [
                {
                    "id": bot.unique_id,
                    "position": { "x": bot.pos[0], "z": bot.pos[1] },
                    "has_pallet": bot.hasPallete,
                    "is_picking": bool(bot.path and bot.target and bot.pos == bot.target[0]),
                    "is_dropping": bool(bot.path and bot.target and bot.pos == bot.target[-1] and not bot.hasPallete)
                }
                for bot in self.bots
            ]
            racks_data = [
                {
                    #"id": rack[0],
                    "position": { "x": rack[1][0], "z": rack[1][1] },
                    "pallets": rack[2]
                }
                for rack in self.racks
            ]
            steps_data.append({
                "step": step,
                "agents": agents_data,
                "racks": racks_data
            })
        
        output_path = "simulation_results.json"
        with open(output_path, 'w') as json_file:
            json.dump(steps_data, json_file, indent=2)
        print(f"[DEBUG] JSON generado en {output_path}")

    def add_bot(self, bot):
        self.bots.append(bot)
        #print(f"[DEBUG] Bot añadido: ID={bot.unique_id}, posición inicial={bot.pos}")
        
    def add_rack(self, id, pos):
        self.racks.append((id, pos, 0))
        #print(f"[DEBUG] Rack añadido: ID={id}, posición={pos}")
        
    def add_tasks(self):
        while self.tasks.qsize() < len(self.bots) * 2:  # Generar nuevas tareas
            print("[DEBUG] Generando nuevas tareas...")

            # random from 1 to 55
            rand_num = random.randint(1, 55)
            
            if rand_num <= 20:
                self.assign_tasks({"task": "entrada-rack"})
            elif rand_num <= 45:
                self.assign_tasks({"task": "rack-salida"})
            else:
                self.assign_tasks({"task": "entrada-salida"})

    def assign_tasks(self, task):
        self.tasks.put(task)
        #print(f"[DEBUG] Tarea asignada: {task}")
    
    def calc_distance(self, pos1, pos2):
        distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        #print(f"[DEBUG] Calculando distancia entre {pos1} y {pos2}: {distance}")
        return distance
    
    def closest_rack(self, bot):
        print(f"[DEBUG] Buscando rack más cercano para bot ID={bot.unique_id}")
        bot_pos = bot.pos
        eligible_racks = [rack for rack in self.racks if rack[2] < 3]
        #print(f"[DEBUG] Racks elegibles: {eligible_racks}")
        
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
        print(f"[DEBUG] Rack más cercano encontrado: {closest_rack['rack']}, Pallets actuales: {closest_rack['rack'][2]}")
        # Actualizar el rack directamente en self.racks
        for i, rack in enumerate(self.racks):
            if rack[0] == closest_rack["rack"][0]:
                self.racks[i] = (rack[0], rack[1], rack[2] + 1)  # Incrementar pallets
                print(f"[DEBUG] Rack actualizado: {self.racks[i]}")
                break
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
            bot_pos = bot.pos
            for rack in racks_with_pallets:
                distance = self.calc_distance(bot_pos, rack[1])
                if distance < min_distance:
                    min_distance = distance
                    closest_bot = bot
                    closest_rack = rack

        print(f"[DEBUG] Bot más cercano: Bot {closest_bot.unique_id}, Rack más cercano: {closest_rack}")
            # Actualizar el rack seleccionado en self.racks
        if closest_rack:
            for i, rack in enumerate(self.racks):
                if rack[0] == closest_rack[0]:
                    self.racks[i] = (rack[0], rack[1], rack[2] - 1)  # Restar 1 pallet
                    print(f"[DEBUG] Rack actualizado tras asignación: {self.racks[i]}")
                    break

        return closest_bot.unique_id, closest_rack

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
        if self.current_step*0.1 >= self.time: # terminar simulación
            self.generate_json()
            self.done = True
            print("[DEBUG] Tiempo límite alcanzado. Finalizando simulación.")
            return

        self.add_tasks()

        print(f"[DEBUG] Total de tareas en cola: {self.tasks.qsize()}")

        # checar si hay bots sin tasks
        available_bots = []
        for bot in self.bots:
            if bot.hasTask == False:
                available_bots.append(bot)

        print(f"[DEBUG] Bots disponibles: {[(bot.unique_id, bot.pos) for bot in available_bots]}")

        # Asignar tareas a los bots disponibles
        if available_bots:
            print(f"[DEBUG] Asignando tareas a {len(available_bots)} bots disponibles...")
            if len(available_bots) > 1:  # Más de un bot disponible
                while available_bots:
                    if self.tasks.empty():
                        self.add_tasks()
                    current_task = self.tasks.queue[0]  # Consultar la tarea en la parte frontal de la cola
                    print(f"[DEBUG] Evaluando tarea: {current_task}")
                    if current_task["task"] == "entrada-salida":
                        best = self.eucladian_distance(available_bots, self.cords["entrada"])
                        bot = available_bots[best]
                        bot.asign_task(target=[self.cords["entrada"], self.cords["salida"]])
                        print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-salida")
                        available_bots.remove(bot)
                        self.tasks.get()  # Eliminar la tarea de la cola
                    elif current_task["task"] == "entrada-rack":
                        best = self.eucladian_distance(available_bots, self.cords["entrada"])
                        bot = available_bots[best]
                        rack = self.closest_rack(bot)
                        if rack:
                            print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-rack con rack ID={rack[0]}")
                            bot.asign_task(target=[self.cords["entrada"], rack[1]])
                            available_bots.remove(bot)
                            self.tasks.get()  # Eliminar la tarea de la cola
                        else:
                            print("[DEBUG] No hay racks disponibles para entrada-rack.")
                    else:
                        result = self.find_nearest_bot_to_pallet(available_bots)
                        
                        if result:
                            closest_bot, closest_rack = result # closest_bot es el ID del bot o el indice del bot en la lista de bots
                            print(f"[DEBUG] Bot {closest_bot} asignado a rack-salida con rack ID={closest_rack[0]}")
                            bot = self.bots[closest_bot]
                            bot.asign_task(target=[closest_rack[1], self.cords["salida"]])
                            available_bots.remove(bot)
                            self.tasks.get()  # Eliminar la tarea de la cola
                        else:
                            print("[DEBUG] No hay racks disponibles con pallets.")
                            self.tasks.get()  # Eliminar la tarea de la cola y continuar

            else:  # Solo un bot disponible
                if self.tasks.empty():
                    self.add_tasks()
                bot = available_bots[0]
                current_task = self.tasks.queue[0]
                print(f"[DEBUG] Evaluando tarea: {current_task}")
                if current_task["task"] == "entrada-salida":
                    bot.asign_task(target=[self.cords["entrada"], self.cords["salida"]])
                    print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-salida")
                    available_bots.remove(bot)
                    self.tasks.get()  # Eliminar la tarea de la cola
                elif current_task["task"] == "entrada-rack":
                    rack = self.closest_rack(bot)
                    if rack:
                        print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-rack con rack ID={rack[0]}")
                        bot.asign_task(target=[self.cords["entrada"], rack[1]])
                        available_bots.remove(bot)
                        self.tasks.get()  # Eliminar la tarea de la cola
                    else:
                        print("[DEBUG] No hay racks disponibles para entrada-rack.")
                else: # todo checar
                    result = self.find_nearest_bot_to_pallet(available_bots)
                        
                    if result:
                        closest_bot, closest_rack = result # closest_bot es el ID del bot o el indice del bot en la lista de bots
                        print(f"[DEBUG] Bot {closest_bot} asignado a rack-salida con rack ID={closest_rack[0]}")
                        bot = self.bots[closest_bot]
                        bot.asign_task(target=[closest_rack[1], self.cords["salida"]])
                        available_bots.remove(bot)
                        self.tasks.get()  # Eliminar la tarea de la cola
                    else:
                        print("[DEBUG] No hay racks disponibles con pallets.")
                        self.tasks.get()  # Eliminar la tarea de la cola y continuar
        # Manejar bots ocupados o en movimiento
        else:
            print("[DEBUG] Verificando próximas posiciones de los bots...")
            next_posArr = []
            for bot in self.bots:
                next_pos = bot.getNextPos()
                print(f"[DEBUG] Bot {bot.unique_id} próxima posición: {next_pos}")
                if next_pos:
                    next_posArr.append(next_pos)
            print(f"[DEBUG] Próximas posiciones: {next_posArr}")
            
            botToStop = None
            otherBot = None

            duplicates = {pos for pos in next_posArr if next_posArr.count(pos) > 1}

            if not duplicates:
                # check if currPos of any is the same as nextPos of another
                for i, bot in enumerate(self.bots):
                    for j, bBot in enumerate(self.bots):
                        if i != j and bot.pos == bBot.getNextPos():
                            #bot.recalcAstar([bot.pos, bBot.pos])
                            # find direction of collision for bot
                            # if bot is moving up and other bot is moving down, check if left or right is free for bot to make path like left, up, right and continue path
                            # if bot is moving left and other bot is moving right, check if up or down is free for bot to make path like up, left, down and continue path
                            # if bot is moving down and other bot is moving up, check if left or right is free for bot to make path like left, down, right and continue path
                            # if bot is moving right and other bot is moving left, check if up or down is free for bot to make path like up, right, down and continue path
                            bot_direction = (bot.getNextPos()[0] - bot.pos[0], bot.getNextPos()[1] - bot.pos[1])
                            bBot_direction = (bBot.getNextPos()[0] - bBot.pos[0], bBot.getNextPos()[1] - bBot.pos[1])
                            
                            # if theyre not face to face continue
                            #if (bot_direction[0] != 0 and bBot_direction[0] == 0) or (bot_direction[1] != 0 and bBot_direction[0] == 0) or (bBot_direction[0] != 0 and bot_direction[0] == 0) or (bBot_direction[1] != 0 and bot_direction[0] == 0):
                            #    break
                            
                            # objectpos checking racks and coords
                            objectPos = set()
                            for rack in self.racks:
                                objectPos.add(rack[1])
                            objectPos.add(self.cords["entrada"])
                            objectPos.add(self.cords["salida"])
                            
                            alternative_paths = []
                            
                            nextP = bot.getNextPos()
                            
                            if (bot_direction == (0, -1) and bBot_direction == (0, 1)) or (bot_direction == (0, 1) and bBot_direction == (0, -1)):  # vertical crash
                                # check if left or right is free checking objectPos
                                if (bot.pos[0] - 1, bot.pos[1]) not in objectPos:
                                    alternative_paths = [(bot.pos[0] - 1, bot.pos[1]), bot.pos] # left -> right
                                elif (bot.pos[0] + 1, bot.pos[1]) not in objectPos:
                                    alternative_paths = [(bot.pos[0] + 1, bot.pos[1]), bot.pos] # right -> left
                                    
                                print(f"[DEBUG] Vertical crash detected. Bot {bot.unique_id} rerouting")
                                
                            elif (bot_direction == (-1, 0) and bBot_direction == (1, 0)) or (bot_direction == (1, 0) and bBot_direction == (-1, 0)):  # horizontal crash
                                # check if up or down is free checking objectPos
                                if (bot.pos[0], bot.pos[1] - 1) not in objectPos:
                                    alternative_paths = [(bot.pos[0], bot.pos[1] + 1), bot.pos] # down -> up
                                elif (bot.pos[0], bot.pos[1] + 1) not in objectPos:
                                    alternative_paths = [(bot.pos[0], bot.pos[1] - 1), bot.pos] # up -> down
                                    
                                print(f"[DEBUG] Horizontal crash detected. Bot {bot.unique_id} rerouting")
                            
                            if alternative_paths:
                                newPath = queue.Queue()
                                newPath.put(alternative_paths[0])
                                newPath.put(alternative_paths[1])
                                
                                while(bot.path.qsize() > 0):
                                    newPath.put(bot.path.get())
                                bot.path = newPath
                                print(f"[DEBUG] Bot {bot.unique_id} rerouted")
                            
                            #otherBot = bBot
                            break
            else:
                print(f"[DEBUG] Colisiones detectadas: {duplicates} de nextPos")
                # stop one bot with duplicate next pos and step the other
                botsWithDup = [bot for bot in self.bots if bot.getNextPos() in duplicates]
                
                if botsWithDup:
                    print(f"[DEBUG] Bots con próxima posición duplicada: {[bot.unique_id for bot in botsWithDup]}")
                    botToStop = botsWithDup[0]
                    print(f"[DEBUG] Bot {botToStop.unique_id} detenido")
                    
            # di cuales bots no jalan
            if botToStop:
                print(f"[DEBUG] Bot {botToStop.unique_id} detenido")
                
            # if otherBot:
            #     print(f"[DEBUG] Otro bot {otherBot.unique_id} detenido")     
            
            for bot in self.bots:
                if bot != botToStop:
                    bot.step()
                    print(f"[DEBUG] Bot {bot.unique_id} avanzó a {bot.pos}")
             
            
            # if len(set(next_posArr)) != len(next_posArr):
            #     print("[DEBUG] Colisiones detectadas. Resolviendo...")
            #     coords, indexes = self.check_collision(next_posArr)
            #     for i in indexes:
            #         print(f"[DEBUG] Bot {self.bots[i].unique_id} avanzando a {coords[i]}")
            #         self.bots[i].step()
            # else:
            #     for bot in self.bots:
            #         bot.step()
            #         print(f"[DEBUG] Bot {bot.unique_id} avanzó a {bot.pos}")

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
        self.grid = [[1 if char in {'M', 'S', 'U', 'J', 'I', 'O'} else 0 for char in row] for row in self.map]

    def astar(self, start, end, otherBotsPositions=None):
        """
        Implementación mejorada del algoritmo A* con inversión del eje Y.
        """
        # Invertir coordenadas Y para trabajar con la representación invertida
        inverted_start = (start[0], len(self.map) - 1 - start[1])
        inverted_end = (end[0], len(self.map) - 1 - end[1])

        # Ajustar el destino si es un rack
        if self.map[inverted_end[1]][inverted_end[0]] == 'S':
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dx, dy in directions:
                nx, ny = inverted_end[0] + dx, inverted_end[1] + dy
                if 0 <= nx < len(self.map[0]) and 0 <= ny < len(self.map) and self.map[ny][nx] == '-':
                    inverted_end = (nx, ny)
                    break

        # Validar inicio y fin
        if self.map[inverted_start[1]][inverted_start[0]] in {'M', 'S', 'U', 'J', 'I', 'O'}:
            print(f"[ASTAR] El punto inicial está bloqueado. {self.map[start[1]][start[0]]}, {start}")
            return queue.Queue()
        if self.map[inverted_end[1]][inverted_end[0]] in {'M', 'S', 'U', 'J', 'I', 'O'}:
            print("[DEBUG] El destino está bloqueado. {self.map[end[1]][end[0]]}, {end}")
            return queue.Queue()

        # Convertir el mapa en binario
        grid = self.grid
        
        # Heurística de Manhattan
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # Inicialización
        open_set = []
        heapq.heappush(open_set, (0, inverted_start))
        came_from = {}
        g_score = {inverted_start: 0}
        f_score = {inverted_start: heuristic(inverted_start, inverted_end)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == inverted_end:
                path = []  # Agregar la coordenada inicial del bot como primer paso
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(inverted_start)
                path.reverse()

                # Reconstruir camino con las coordenadas originales (invirtiendo Y nuevamente)
                queue_path = queue.Queue()
                for step in path:
                    original_step = (step[0], len(self.map) - 1 - step[1])
                    queue_path.put(original_step)
                return queue_path

            neighbors = [
                (current[0] + dx, current[1] + dy)
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
            ]
            for neighbor in neighbors:
                if 0 <= neighbor[0] < len(grid[0]) and 0 <= neighbor[1] < len(grid) and grid[neighbor[1]][neighbor[0]] == 0:
                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + heuristic(neighbor, inverted_end)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        print("[DEBUG] No se encontró camino")
        return queue.Queue()




    def getNextPos(self):
        return self.path.queue[0] if not self.path.empty() else None
    
    def recalcAstar(self, otherBotsPositions):
        if not self.path.empty():
            new_path = self.astar(self.pos, self.target[0], otherBotsPositions)
            self.path = new_path
            print(f"[BOT] Bot ID={self.unique_id} recalculando path {list(self.path.queue)}")

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
                next_pos = self.path.get()
                self.model.grid.remove_agent(self)
                self.pos = next_pos
                print(f"[BOT] Bot ID={self.unique_id} avanzando a {self.pos}")
                if self.path.empty() and len(self.target) > 1: # llegó al destino y aun tiene otro target
                    # checar si llegó a un rack
                    #if self.pos not in self.cords["entrada"] and self.pos not in self.cords["salida"]:




                    self.target.pop(0)
                    self.path = self.astar(self.pos, self.target[0])
                    self.hasPallete = True # en el primer target siempre recoge un pallete
                elif self.path.empty() and len(self.target) == 1: # ya es su ultimo target
                    # checar si llegó a un rack
                    
                    self.hasTask = False
                    self.hasPallete = False
                    self.target = []
                self.model.grid.move_agent(self, self.pos)


        else:
            print(f"[BOT] Step del bot ID={self.unique_id} sin tarea")
            # si no tiene una tarea asignada, esperar
            pass





    @staticmethod
    def from_txt_to_desc(file_path):
        try:
            with open(file_path, 'r') as file:
                desc = [line.strip() for line in file.readlines()]
            # Find the position of 'I'
            for row_index, line in enumerate(desc):
                col_index = line.find('I')
                if col_index != -1:
                    print(f"Position of 'I': Row={row_index}, Col={col_index}")
            return desc
        except Exception as e:
            print(f"Error reading the file: {e}")
            return None

    def read_map(self):
        desc_file = "maze.txt"
        root_path = os.path.dirname(os.path.abspath(__file__))
        desc = self.from_txt_to_desc(root_path + "/" + desc_file)
        # write desc to file
        with open(root_path + "/output.txt", 'w') as output_file:
            for line in desc:
                output_file.write(f"{line}\n")
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
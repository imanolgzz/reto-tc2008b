from mesa.agent import Agent
from collections import defaultdict, deque
import queue
import heapq
import os
import random
import json
import matplotlib.pyplot as plt
import numpy as np

class LGVManager(Agent):
    def __init__(self, unique_id, model, time):
        super().__init__(unique_id, model)
        self.bots = []
        self.cords = {}
        self.tasks = queue.Queue()
        self.current_step = 0
        self.racks = []
        self.time = time*60
        #self.time = time*10
        self.done = False
        ##print(f"[DEBUG] LGVManager inicializado con tiempo límite: {self.time} segundos")
        self.info = {}
        self.accTime = 0
        
        self.historic_battery = []
        self.steps_without_mission = [0, 0, 0]
        self.assigned_tasks = ["", "", ""]
        # self.ended_entrada_rack = []
        # self.ended_rack_salida = []
        # self.ended_entrada_salida = []
        self.ended = {"entrada-rack": [], "rack-salida": [], "entrada-salida": []}
        

    def add_bot(self, bot):
        bot.cords = self.cords
        self.bots.append(bot)
        ##print(f"[DEBUG] Bot añadido: ID={bot.unique_id}, posición inicial={bot.pos}")
        
    def add_rack(self, id, pos):
        self.racks.append((id, pos, random.randint(0, 3)))  # ID, posición, pallets
        ##print(f"[DEBUG] Rack añadido: ID={id}, posición={pos}")
        
    def add_tasks(self):
        while self.tasks.qsize() < len(self.bots) * 2:  # Generar nuevas tareas
            #print("[DEBUG] Generando nuevas tareas...")

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
        ##print(f"[DEBUG] Tarea asignada: {task}")
    
    def calc_distance(self, pos1, pos2):
        distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        ##print(f"[DEBUG] Calculando distancia entre {pos1} y {pos2}: {distance}")
        return distance
    
    def closest_rack(self, bot_pos):
        #print(f"[DEBUG] Buscando rack más cercano a la posición del bot: {bot_pos}")
        eligible_racks = [rack for rack in self.racks if rack[2] < 3]
        ##print(f"[DEBUG] Racks elegibles: {eligible_racks}")
        
        if not eligible_racks:
            #print("[DEBUG] No hay racks elegibles disponibles")
            return None
        
        distances = [
            {
                "rack": rack,
                "distance": self.calc_distance(bot_pos, rack[1])
            }
            for rack in eligible_racks
        ]
        
        occupied_racks = [bot.currRack for bot in self.bots if bot.currRack]

        #closest_rack = min(distances, key=lambda d: d["distance"])
        closest_rack = None
        min_distance = float('inf')

        # Iterar sobre racks elegibles y verificar ocupación
        for distance_info in distances:
            rack = distance_info["rack"]
            distance = distance_info["distance"]

            if rack[0] not in occupied_racks and distance < min_distance:
                closest_rack = rack
                min_distance = distance

        

        #print(f"[DEBUG] Rack más cercano encontrado: {closest_rack['rack']}, Pallets actuales: {closest_rack['rack'][2]}")
        # Actualizar el rack directamente en self.racks
        # for i, rack in enumerate(self.racks):
        #     if rack[0] == closest_rack["rack"][0]:
        #         #self.racks[i] = (rack[0], rack[1], rack[2] + 1)  # Incrementar pallets
        #         #print(f"[DEBUG] Rack actualizado: {self.racks[i]}")
        #         break
        return closest_rack
    
    def find_nearest_bot_to_pallet(self, available_bots):
        #print(f"[DEBUG] Buscando bot más cercano a un rack con pallets disponibles")
        racks_with_pallets = [rack for rack in self.racks if rack[2] > 0]
        #print(f"[DEBUG] Racks con pallets: {racks_with_pallets}")

        if not racks_with_pallets:
            #print("[DEBUG] No hay racks con pallets disponibles")
            return None

        closest_bot = None
        closest_rack = None
        min_distance = float('inf')
        
        occupied_racks = [bot.currRack for bot in self.bots if bot.currRack]

        for bot in available_bots:
            bot_pos = bot.pos
            
            for rack in racks_with_pallets:
                if rack[0] not in occupied_racks:
                    distance = self.calc_distance(bot_pos, rack[1])
                    if distance < min_distance:
                        min_distance = distance
                        closest_bot = bot
                        closest_rack = rack
                # distance = self.calc_distance(bot_pos, rack[1])
                # if distance < min_distance:
                #     min_distance = distance
                #     closest_bot = bot
                #     closest_rack = rack
                    

        #print(f"[DEBUG] Bot más cercano: Bot {closest_bot.unique_id}, Rack más cercano: {closest_rack}")
            # Actualizar el rack seleccionado en self.racks
        if closest_rack:
            for i, rack in enumerate(self.racks):
                if rack[0] == closest_rack[0]:
                    #self.racks[i] = (rack[0], rack[1], rack[2] - 1)  # Restar 1 pallet
                    #print(f"[DEBUG] Rack actualizado tras asignación: {self.racks[i]}")
                    break

        return closest_bot.unique_id, closest_rack

    def check_collision(self, next_pos):
        #print(f"[DEBUG] Comprobando colisiones para posiciones: {next_pos}")
        indices = defaultdict(list)

        for index, coord in enumerate(next_pos):
            indices[coord].append(index)

        duplicates = {coord: idx_list for coord, idx_list in indices.items() if len(idx_list) > 1}
        #if duplicates:
            #print(f"[DEBUG] Colisiones detectadas: {duplicates}")
        
        selected_coords = []
        selected_indices = []
        seen_coords = set()

        for index, coord in enumerate(next_pos):
            if coord not in seen_coords:
                selected_coords.append(coord)
                selected_indices.append(index)
                seen_coords.add(coord)

        #print(f"[DEBUG] Coordenadas seleccionadas: {selected_coords}, Índices: {selected_indices}")
        return selected_coords, selected_indices

    def eucladian_distance(self, bots, dest):
        #print(f"[DEBUG] Calculando distancia euclidiana a destino {dest}")
        bot_min_index = None
        min_distance = float('inf')
        for i, bot in enumerate(bots):
            bot_pos = bot.pos
            distance = ((bot_pos[0] - dest[0])**2 + (bot_pos[1] - dest[1])**2)**0.5
            #print(f"[DEBUG] Bot ID={bot.unique_id}, Posición={bot_pos}, Distancia={distance}")
            if distance < min_distance:
                min_distance = distance
                bot_min_index = i
        #print(f"[DEBUG] Bot más cercano: índice={bot_min_index}")
        return bot_min_index
    
    def get_battery_levels(self):
        return {bot.unique_id: bot.battery for bot in self.bots}
    
    def plot_battery_levels(self):        
        # Ensure data consistency
        if not self.historic_battery or len(self.historic_battery[0]) != len(self.bots):
            print("[ERROR] Inconsistent battery data.")
            print(f"[DEBUG] Historic battery data: {self.historic_battery}")
            print(f"[DEBUG] Number of bots: {len(self.bots)}")
            print(f"[DEBUG] Number of battery levels: {len(self.historic_battery[0])}")
            return

        for i, bot in enumerate(self.bots):
            try:
                plt.plot([j[i] for j in self.historic_battery], label=f"Bot {bot.unique_id}")
            except IndexError:
                print(f"[ERROR] IndexError for bot {bot.unique_id} at index {i}.")
                continue
        # makey axis from 0 to 100
        plt.ylim(0.0, 100.0)
        plt.xlabel("Step")
        plt.ylabel("Battery Level (%)")
        plt.title("Battery Levels")
        plt.legend()
        plt.savefig("battery_levels.png")

    def plot_utilisation_percentage(self):
        # bar graph of steps without mission compared to total steps as percentage        
        total_steps = self.current_step
        utilisation_percentage = [(total_steps - steps) / total_steps * 100 for steps in self.steps_without_mission]
        
        bot_labels = ["Bot 0", "Bot 1", "Bot 2"]

        # Increase figure size for better readability
        plt.figure(figsize=(8, 6))
        bars = plt.bar(bot_labels, utilisation_percentage, color=['blue', 'orange', 'green'])

        # Add percentage values above the bars
        for bar, percentage in zip(bars, utilisation_percentage):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{percentage:.1f}%",
                ha='center',
                va='bottom'
            )
        
        plt.xlabel("Bot ID")
        plt.ylabel("Utilisation Percentage (%)")
        plt.title("Utilisation Percentage")
        
        # Rotate x-axis labels if necessary
        plt.xticks(rotation=0)
        
        # Save or display the plot
        plt.tight_layout()
        plt.savefig("utilisation_percentage.png")
        
    #  def plot_finished_task_per_flow_per_hour(self):
    #     # bar graph of tasks finished per flow per hour
    #     #print(f"[DEBUG] Tareas finalizadas por flujo por hora: {self.ended}")
        
    #     # Calculate the number of tasks finished per flow per hour
    #     tasks_per_flow_per_hour = {
    #         flow: len(ended) for flow, ended in self.ended.items()
    #     }
        
    #     #print(f"[DEBUG] Tareas finalizadas por flujo por hora: {tasks_per_flow_per_hour}")
        
    #     # Increase figure size for better readability
    #     plt.figure(figsize=(8, 6))
    #     bars = plt.bar(tasks_per_flow_per_hour.keys(), tasks_per_flow_per_hour.values(), color=['blue', 'orange', 'green'])

    #     # Add values above the bars
    #     for bar, value in zip(bars, tasks_per_flow_per_hour.values()):
    #         plt.text(
    #             bar.get_x() + bar.get_width() / 2,
    #             bar.get_height(),
    #             f"{value}",
    #             ha='center',
    #             va='bottom'
    #         )
        
    #     plt.xlabel("Flow")
    #     plt.ylabel("Tasks Finished")
    #     plt.title("Tasks Finished per Flow per Hour")
        
    #     # Rotate x-axis labels if necessary
    #     plt.xticks(rotation=0)
        
    #     # Save or display the plot
    #     plt.tight_layout()
    #     plt.savefig("tasks_finished_per_flow_per_hour.png")

    def plot_finished_task_per_flow_per_hour(self):
        import numpy as np

        # Group tasks by hour (600 steps = 1 hour)
        tasks_per_flow_per_hour = {}

        for flow, steps in self.ended.items():
            # Create a dictionary where keys are hour intervals and values are task counts
            hourly_counts = {}
            for step in steps:
                hour = step // 3600  # Determine the hour by dividing step by 600
                if hour not in hourly_counts:
                    hourly_counts[hour] = 0
                hourly_counts[hour] += 1
            
            tasks_per_flow_per_hour[flow] = hourly_counts

        # Debug: print the processed data
        print(f"[DEBUG] Tasks finished per flow per hour: {tasks_per_flow_per_hour}")
        
        # Prepare data for plotting
        flows = list(tasks_per_flow_per_hour.keys())
        hours = sorted(set(hour for flow in tasks_per_flow_per_hour.values() for hour in flow.keys()))
        
        # Create a matrix of counts for each flow and hour
        flow_hour_counts = []
        for flow in flows:
            flow_counts = [tasks_per_flow_per_hour[flow].get(hour, 0) for hour in hours]
            flow_hour_counts.append(flow_counts)

        # Plot the bar chart with grouped bars
        x = np.arange(len(hours))  # the label locations (one for each hour)
        width = 0.2  # width of the bars

        plt.figure(figsize=(10, 6))
        for i, (flow, counts) in enumerate(zip(flows, flow_hour_counts)):
            plt.bar(x + i * width, counts, width, label=f"Flow {flow}")

        # Add labels and titles
        plt.xlabel("Hour")
        plt.ylabel("Tasks Finished")
        plt.title("Tasks Finished per Flow per Hour")
        plt.xticks(x + width * (len(flows) - 1) / 2, [f"Hour {hour}" for hour in hours])
        plt.legend()

        # Save or display the plot
        plt.tight_layout()
        plt.savefig("tasks_finished_per_flow_per_hour.png")
        
    
    def generate_json(self):
        # Crear una lista de pasos en lugar de un diccionario
        steps_data = []
        
        for step, data in self.info.items():
            step_entry = {
                "step": step,
                "agents": [
                    {
                        "id": agent["id"],
                        "position": {
                            "x": agent["position"]["x"],
                            "z": agent["position"]["z"]
                        },
                        "has_pallet": agent["has_pallet"]
                    }
                    for agent in data["agents"]
                ],
                "racks": [
                    {\
                        "position": {
                            "x": rack["position"]["x"],
                            "z": rack["position"]["z"]
                        },
                        "pallets": rack["pallets"]
                    }
                    for rack in data["racks"]
                ]
            }
            steps_data.append(step_entry)
        
        # Guardar la lista en un archivo JSON
        output_path = "simulation_results.json"
        with open(output_path, 'w') as json_file:
            json.dump(steps_data, json_file, indent=2)



    def step(self):
        #print(f"\n[STEP {self.current_step}] Iniciando paso del LGVManager")
        if self.current_step*0.1 >= self.time: # terminar simulación
            self.generate_json()
            self.plot_battery_levels()
            self.plot_utilisation_percentage()
            self.plot_finished_task_per_flow_per_hour()
            self.done = True
            print("[END] Tiempo acomulado de palletes en entrada:", self.accTime, "segundos")
            # write to file acc time
            with open("acc_time.txt", "w") as f:
                f.write(f"Tiempo acomulado de palletes en entrada: {self.accTime} segundos")
            return

        self.add_tasks()

        #print(f"[DEBUG] Total de tareas en cola: {self.tasks.qsize()}")

        # checar si hay bots sin tasks
        available_bots = []
        for bot in self.bots:
            if bot.hasTask == False and bot.charging == False:
                available_bots.append(bot)

        #print(f"[DEBUG] Bots disponibles: {[(bot.unique_id, bot.pos) for bot in available_bots]}")
        
        
        modified_racks = []
        # checar si un bot acaba de hacer algo con rack
        for bot in self.bots:
            if bot.currRack:
                #print(f"[DEBUG] Bot {bot.unique_id} con rack ID={bot.currRack[0]}")
                if bot.pickRack and bot.count == 59:
                    for i, rack in enumerate(self.racks):
                        if rack[0] == bot.currRack[0]:
                            self.racks[i] = (rack[0], rack[1], rack[2] - 1)
                            modified_racks.append(self.racks[i])
                            bot.currRack = None
                            break
                    #print(f"[DEBUG] Bot {bot.unique_id} dejando pallet")
                elif bot.dropRack and bot.count == 59:
                    for i, rack in enumerate(self.racks):
                        if rack[0] == bot.currRack[0]:
                            self.racks[i] = (rack[0], rack[1], rack[2] + 1)
                            modified_racks.append(self.racks[i])
                            bot.currRack = None
                            break
                    #print(f"[DEBUG] Bot {bot.unique_id} dejó pallet")
        
        # checar if available bots tienen menos de 70% de batería
        for bot in available_bots:
            if bot.battery < 70:
                bot.asign_task(target=[self.cords[f"cargador{bot.unique_id}"]])
                bot.charging = True
                print(f"[DEBUG URGENTE] Bot {bot.unique_id} cargando batería")
                
        
        # checar si bots no estan haciendo nada
        for bot in self.bots:
            if bot.hasTask == False:
                if self.assigned_tasks[bot.unique_id] != "":
                    self.ended[self.assigned_tasks[bot.unique_id]].append(self.current_step)
                    self.assigned_tasks[bot.unique_id] = ""
                self.steps_without_mission[bot.unique_id] += 1
                
        

        # Asignar tareas a los bots disponibles
        if available_bots:
            #print(f"[DEBUG] Asignando tareas a {len(available_bots)} bots disponibles...")
            if len(available_bots) > 1:  # Más de un bot disponible
                while available_bots:
                    if self.tasks.empty():
                        self.add_tasks()
                    current_task = self.tasks.queue[0]  # Consultar la tarea en la parte frontal de la cola
                    #print(f"[DEBUG] Evaluando tarea: {current_task}")
                    if current_task["task"] == "entrada-salida":
                        best = self.eucladian_distance(available_bots, self.cords["entrada1"])
                        bot = available_bots[best]
                        bot.asign_task(target=[self.cords[f"entrada{bot.unique_id}"], self.cords[f"salida{bot.unique_id}"]])
                        self.assigned_tasks[bot.unique_id] = "entrada-salida"
                        #print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-salida")
                        available_bots.remove(bot)
                        self.tasks.get()  # Eliminar la tarea de la cola
                    elif current_task["task"] == "entrada-rack":
                        best = self.eucladian_distance(available_bots, self.cords["entrada1"])
                        bot = available_bots[best]
                        rack = self.closest_rack(self.cords[f"entrada{bot.unique_id}"])
                        if rack:
                            #print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-rack con rack ID={rack[0]}")
                            bot.asign_task(target=[self.cords[f"entrada{bot.unique_id}"], rack[1]])
                            self.assigned_tasks[bot.unique_id] = "entrada-rack"
                            bot.currRack = rack
                            available_bots.remove(bot)
                            self.tasks.get()  # Eliminar la tarea de la cola
                        #else:
                            #print("[DEBUG] No hay racks disponibles para entrada-rack.")
                    else:
                        result = self.find_nearest_bot_to_pallet(available_bots)
                        
                        if result:
                            closest_bot, closest_rack = result # closest_bot es el ID del bot o el indice del bot en la lista de bots
                            #print(f"[DEBUG] Bot {closest_bot} asignado a rack-salida con rack ID={closest_rack[0]}")
                            bot = self.bots[closest_bot]
                            bot.asign_task(target=[closest_rack[1], self.cords[f"salida{bot.unique_id}"]])
                            self.assigned_tasks[bot.unique_id] = "rack-salida"
                            bot.currRack = closest_rack
                            available_bots.remove(bot)
                            self.tasks.get()  # Eliminar la tarea de la cola
                        else:
                            #print("[DEBUG] No hay racks disponibles con pallets.")
                            self.tasks.get()  # Eliminar la tarea de la cola y continuar

            else:  # Solo un bot disponible
                if self.tasks.empty():
                    self.add_tasks()
                bot = available_bots[0]
                current_task = self.tasks.queue[0]
                #print(f"[DEBUG] Evaluando tarea: {current_task}")
                if current_task["task"] == "entrada-salida":
                    self.accTime += bot.asign_task(target=[self.cords[f"entrada{bot.unique_id}"], self.cords[f"salida{bot.unique_id}"]])
                    self.assigned_tasks[bot.unique_id] = "entrada-salida"
                    #print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-salida")
                    available_bots.remove(bot)
                    self.tasks.get()  # Eliminar la tarea de la cola
                elif current_task["task"] == "entrada-rack":
                    rack = self.closest_rack(self.cords[f"entrada{bot.unique_id}"])
                    if rack:
                        #print(f"[DEBUG] Bot {bot.unique_id} asignado a entrada-rack con rack ID={rack[0]}")
                        self.accTime += bot.asign_task(target=[self.cords[f"entrada{bot.unique_id}"], rack[1]])
                        self.assigned_tasks[bot.unique_id] = "entrada-rack"
                        bot.currRack = rack
                        available_bots.remove(bot)
                        self.tasks.get()  # Eliminar la tarea de la cola
                    #else:
                        #print("[DEBUG] No hay racks disponibles para entrada-rack.")
                else: # todo checar
                    result = self.find_nearest_bot_to_pallet(available_bots)
                        
                    if result:
                        closest_bot, closest_rack = result # closest_bot es el ID del bot o el indice del bot en la lista de bots
                        #print(f"[DEBUG] Bot {closest_bot} asignado a rack-salida con rack ID={closest_rack[0]}")
                        bot = self.bots[closest_bot]
                        bot.asign_task(target=[closest_rack[1], self.cords[f"salida{bot.unique_id}"]])
                        self.assigned_tasks[bot.unique_id] = "rack-salida"
                        bot.currRack = closest_rack
                        available_bots.remove(bot)
                        self.tasks.get()  # Eliminar la tarea de la cola
                    else:
                        #print("[DEBUG] No hay racks disponibles con pallets.")
                        self.tasks.get()  # Eliminar la tarea de la cola y continuar
        # Manejar bots ocupados o en movimiento
        else:
            #print("[DEBUG] Verificando próximas posiciones de los bots...")
            next_posArr = []
            for bot in self.bots:
                next_pos = bot.getNextPos()
                #print(f"[DEBUG] Bot {bot.unique_id} próxima posición: {next_pos}")
                if next_pos and not bot.static:
                    next_posArr.append(next_pos)
            #print(f"[DEBUG] Próximas posiciones: {next_posArr}")
            
            botToStop = None
            #otherBot = None

            duplicates = {pos for pos in next_posArr if next_posArr.count(pos) > 1}

            if not duplicates:
                # check if currPos of any is the same as nextPos of another
                for i, bot in enumerate(self.bots):
                    for j, bBot in enumerate(self.bots):
                        if i != j and bot.pos == bBot.getNextPos():
                            #bot.recalcAstar([bot.pos, bBot.pos])
                            # find direction of collision for bot
                            bot_direction = (bot.getNextPos()[0] - bot.pos[0], bot.getNextPos()[1] - bot.pos[1])
                            bBot_direction = (bBot.getNextPos()[0] - bBot.pos[0], bBot.getNextPos()[1] - bBot.pos[1])
                            
                            if bot.static:
                                # move other
                                bBot.recalcAstar(bot.pos)
                                break
                            if bBot.static: # todo creo que no
                                # move bot
                                bot.recalcAstar(bBot.pos)
                                break
                            
                            # objectpos checking racks and coords
                            objectPos = set()
                            for rack in self.racks:
                                objectPos.add(rack[1])
                            # objectPos.add(self.cords["entrada0"])
                            # objectPos.add(self.cords["salida0"])
                            
                            alternative_paths = []
                            
                            nextP = bot.getNextPos()
                            
                            if (bot_direction == (0, -1) and bBot_direction == (0, 1)) or (bot_direction == (0, 1) and bBot_direction == (0, -1)):  # vertical crash
                                # check if left or right is free checking objectPos
                                if (bot.pos[0] - 1, bot.pos[1]) not in objectPos:
                                    alternative_paths = [(bot.pos[0] - 1, bot.pos[1]), bot.pos] # left -> right
                                elif (bot.pos[0] + 1, bot.pos[1]) not in objectPos:
                                    alternative_paths = [(bot.pos[0] + 1, bot.pos[1]), bot.pos] # right -> left
                                    
                                #print(f"[DEBUG] Vertical crash detected. Bot {bot.unique_id} rerouting")
                                
                            elif (bot_direction == (-1, 0) and bBot_direction == (1, 0)) or (bot_direction == (1, 0) and bBot_direction == (-1, 0)):  # horizontal crash
                                # check if up or down is free checking objectPos
                                if (bot.pos[0], bot.pos[1] - 1) not in objectPos:
                                    alternative_paths = [(bot.pos[0], bot.pos[1] - 1), bot.pos] # down -> up
                                elif (bot.pos[0], bot.pos[1] + 1) not in objectPos:
                                    alternative_paths = [(bot.pos[0], bot.pos[1] + 1), bot.pos] # up -> down
                                    
                                #print(f"[DEBUG] Horizontal crash detected. Bot {bot.unique_id} rerouting")
                            
                            if alternative_paths:
                                newPath = queue.Queue()
                                newPath.put(alternative_paths[0])
                                newPath.put(alternative_paths[1])
                                
                                while(bot.path.qsize() > 0):
                                    newPath.put(bot.path.get())
                                bot.path = newPath
                                #print(f"[DEBUG] Bot {bot.unique_id} rerouted")
                            
                            #otherBot = bBot
                            break
            else:
                #print(f"[DEBUG] Colisiones detectadas: {duplicates} de nextPos")
                # stop one bot with duplicate next pos and step the other
                botsWithDup = [bot for bot in self.bots if bot.getNextPos() in duplicates]
                
                if botsWithDup:
                    #print(f"[DEBUG] Bots con próxima posición duplicada: {[bot.unique_id for bot in botsWithDup]}")
                    botToStop = botsWithDup[0]
                    #print(f"[DEBUG] Bot {botToStop.unique_id} detenido")
                    
            # di cuales bots no jalan
            #if botToStop:
                #print(f"[DEBUG] Bot {botToStop.unique_id} detenido")
                
            # if otherBot:
            #     #print(f"[DEBUG] Otro bot {otherBot.unique_id} detenido")     
            
            for bot in self.bots:
                if bot != botToStop:
                    bot.step()
                    #print(f"[DEBUG] Bot {bot.unique_id} avanzó a {bot.pos}")
        
        if self.current_step == 0:
            self.info.update({self.current_step: {"agents": [{"id": bot.unique_id, "position": {"x": bot.pos[0], "z": bot.pos[1]}, "has_pallet": bot.hasPallete } for bot in self.bots], "racks": [{"id": rack[0], "position": {"x": rack[1][0], "z": rack[1][1]}, "pallets": rack[2]} for rack in self.racks]}})
        else:
            self.info.update({self.current_step: {"agents": [{"id": bot.unique_id, "position": {"x": bot.pos[0], "z": bot.pos[1]}, "has_pallet": bot.hasPallete } for bot in self.bots], "racks": [{"id": rack[0], "position": {"x": rack[1][0], "z": rack[1][1]}, "pallets": rack[2]} for rack in modified_racks]}})
                
        self.historic_battery.append([bot.battery for bot in self.bots])
                
        self.current_step += 1
        
        #print(f"[STEP {self.current_step}] Finalizando paso del LGVManager\n")


        

        
        
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
        self.cords = {}
        self.currRack = None
        self.currStep = -1
        
        self.static = False
        self.pickIn = False
        self.dropOut = False
        self.pickRack = False
        self.dropRack = False
        self.count = 0
        
        self.battery = 100
        self.charging = False

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
            #print(f"[ASTAR] El punto inicial está bloqueado. {self.map[start[1]][start[0]]}, {start}")
            return queue.Queue()
        if self.map[inverted_end[1]][inverted_end[0]] in {'M', 'S', 'U', 'J', 'I', 'O'}:
            #print("[DEBUG] El destino está bloqueado. {self.map[end[1]][end[0]]}, {end}")
            return queue.Queue()

        # Convertir el mapa en binario
        grid = self.grid
        
        # Evitar colisiones con otros bots
        if otherBotsPositions:
            #print(f"[DEBUG URGENT] Evitando colisiones con otros bots: {otherBotsPositions[0]}, {otherBotsPositions[1]}. Grid: {len(grid)}x{len(grid[0])}") #96x80 90x115
            otherBotsPositions = (otherBotsPositions[0], len(grid) - 1 - otherBotsPositions[1])
            grid[otherBotsPositions[1]][otherBotsPositions[0]] = 1
        
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

        #print("[DEBUG] No se encontró camino")
        return queue.Queue()


    def getNextPos(self):
        return self.path.queue[0] if not self.path.empty() else None
    
    def recalcAstar(self, otherBotsPositions):
        new_path = self.astar(self.pos, self.target[0], otherBotsPositions)
        self.path = new_path
        #print(f"[BOT] Bot ID={self.unique_id} recalculando path {list(self.path.queue)}")

    def asign_task(self, target):
        for cord in target:
            self.target.append(cord)
        #print(f"[BOT] Bot ID={self.unique_id} asignado a tarea con target {self.target}")
        self.path = self.astar(self.pos, self.target[0]) # usa el primer target 
        #print(f"[BOT] Bot ID={self.unique_id} con path {list(self.path.queue)}")
        self.hasTask = True

        return self.path.qsize()-1

    def step(self):
        self.currStep += 1
        self.static = True
        self.battery -= 1/720
        if self.charging and self.path.empty():
            self.battery += (1/720)
            self.battery += (1/15)
            #print(f"[BOT] Bot ID={self.unique_id} cargando batería. Batería actual: {self.battery}")
            if self.battery == 90:
                self.charging = False
                #print(f"[BOT] Bot ID={self.unique_id} batería cargada al 90%")
        elif self.pickIn:
            self.count += 1
            if self.count == 30:
                self.pickIn = False
                self.hasPallete = True
                self.count = 0
                #print(f"[BOT] Bot ID={self.unique_id} recogió pallet")
        elif self.dropOut:
            self.count += 1
            if self.count == 30:
                self.dropOut = False
                self.hasPallete = False
                self.count = 0
                #print(f"[BOT] Bot ID={self.unique_id} dejó pallet")
        elif self.pickRack:
            self.count += 1
            if self.count == 60:
                self.pickRack = False
                self.hasPallete = True
                self.count = 0
                #print(f"[BOT] Bot ID={self.unique_id} recogió pallet")
        elif self.dropRack:
            self.count += 1
            if self.count == 60:
                self.dropRack = False
                self.hasPallete = False
                self.count = 0
                #print(f"[BOT] Bot ID={self.unique_id} dejó pallet")
        else:
            self.static = False
            self.battery += 1/720
            self.battery -= 1/180
            if self.hasTask:
                #print(f"[BOT] Step del bot ID={self.unique_id} con tarea asignada y posición {self.pos}")

                # si tiene una tarea asignada, moverse a la siguiente posición
                if not self.path.empty(): # aun le quedan pasos por dar
                    next_pos = self.path.get()
                    self.model.grid.remove_agent(self)
                    self.pos = next_pos
                    #print(f"[BOT] Bot ID={self.unique_id} avanzando a {self.pos}")
                    
                    if self.path.empty() and len(self.target) > 1: # llegó al destino y aun tiene otro target
                        # checar si llegó a un rack
                        #if self.pos not in self.cords["entrada"] and self.pos not in self.cords["salida"]:
                        if self.pos == self.cords[f"entrada{self.unique_id}"]:
                            self.pickIn = True
                            #print(f"[BOT] Bot ID={self.unique_id} llegó a entrada y recogerá pallet")
                        else:
                            self.pickRack = True
                            #print(f"[BOT] Bot ID={self.unique_id} llegó a rack y recoge pallet")

                        self.target.pop(0)
                        self.path = self.astar(self.pos, self.target[0])
                        
                    elif self.path.empty() and len(self.target) == 1: # ya es su ultimo target
                        # checar si llegó a un rack
                        
                        if self.pos == self.cords[f"salida{self.unique_id}"]:
                            self.dropOut = True
                            #print(f"[BOT] Bot ID={self.unique_id} llegó a salida y dejará pallet")
                        elif self.pos == self.cords[f"cargador{self.unique_id}"]:
                            print(f"[BOT] Bot ID={self.unique_id} llegó a cargador")
                        else:
                            self.dropRack = True
                            #print(f"[BOT] Bot ID={self.unique_id} llegó a rack y dejará pallet")
                        
                        self.hasTask = False
                        self.hasPallete = False
                        self.target = []
                        
                    self.model.grid.move_agent(self, self.pos)
            else:
                #print(f"[BOT] Step del bot ID={self.unique_id} sin tarea")
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
                #if col_index != -1:
                    #print(f"Position of 'I': Row={row_index}, Col={col_index}")
            return desc
        except Exception as e:
            #print(f"Error reading the file: {e}")
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
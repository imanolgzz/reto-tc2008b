from mesa.agent import Agent
import os

class LGVManager(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        
class LGV(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
    
    
    
    
    
    
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
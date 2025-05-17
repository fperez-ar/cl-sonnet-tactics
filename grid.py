# grid.py
import random

class Grid:
    def __init__(self, config):
        self.cell_size = config['game']['grid']['cell_size']
        self.width = config['game']['grid']['width']
        self.height = config['game']['grid']['height']
        self.terrain_types = config['terrain_types']
        
        # Initialize the grid with random terrain
        self.cells = []
        terrain_list = list(self.terrain_types.keys())
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Randomly choose a terrain type
                terrain = terrain_list[0] #random.choice(terrain_list)
                row.append({'terrain': terrain, 'unit': None})
            self.cells.append(row)
    
    def get_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return None
    
    def place_unit(self, unit, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x]['unit'] = unit
            unit.x, unit.y = x, y
            return True
        return False
    
    def remove_unit(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x]['unit'] = None
            return True
        return False
    
    def move_unit(self, from_x, from_y, to_x, to_y):
        if self.cells[from_y][from_x]['unit'] and not self.cells[to_y][to_x]['unit']:
            unit = self.cells[from_y][from_x]['unit']
            self.cells[to_y][to_x]['unit'] = unit
            self.cells[from_y][from_x]['unit'] = None
            unit.x, unit.y = to_x, to_y
            return True
        return False
    
    def get_terrain_info(self, x, y):
        cell = self.get_cell(x, y)
        if cell:
            terrain_type = cell['terrain']
            return {
                'name': terrain_type,
                'description': self.terrain_types[terrain_type]['description'],
                'movement_cost': self.terrain_types[terrain_type]['movement_cost']
            }
        return None

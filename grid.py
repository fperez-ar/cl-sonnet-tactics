# grid.py
class Grid:
    def __init__(self, config, level_index=0):
        self.cell_size = config['game']['grid']['cell_size']
        self.terrain_types = config['terrain_types']
        self.terrain_mapping = config['terrain_mapping']
        
        # Load level data
        self.levels = config['levels']
        self.current_level = self.levels[level_index]
        self.layout = self.current_level['layout']
        
        # Set grid dimensions based on level layout
        self.height = len(self.layout)
        self.width = len(self.layout[0]) if self.layout else 0
        
        # Initialize the grid from the level layout
        self.cells = []
        self._initialize_grid_from_layout()
        
    
    def _initialize_grid_from_layout(self):
        # Create the grid cells from the layout
        self.cells = []
        
        for y, row in enumerate(self.layout):
            grid_row = []
            for x, char in enumerate(row):
                # Get the terrain type from the mapping
                terrain_type = self.terrain_mapping.get(char, list(self.terrain_types.keys())[0])
                grid_row.append({'terrain': terrain_type, 'unit': None})
            self.cells.append(grid_row)
    
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
    
    def get_level_name(self):
        return self.current_level['name']
    
    def get_level_description(self):
        return self.current_level['description']

    def get_player_start_positions(self):
        """Return the player unit starting positions from the level data."""
        return self.current_level.get('player_units', [])

    def get_enemy_start_positions(self):
        """Return the enemy unit starting positions from the level data."""
        return self.current_level.get('enemy_units', [])


# unit.py
class Unit:
    def __init__(self, unit_type, is_player, config, x=0, y=0):
        self.unit_type = unit_type
        self.is_player = is_player
        self.x = x
        self.y = y
        
        # Load stats from config
        unit_config = config['unit_types'][unit_type]
        self.strength = unit_config['strength']
        self.range = unit_config['range']
        self.max_hp = unit_config['hp']
        self.current_hp = self.max_hp
        self.move_range = unit_config['move']  # New move stat
        self.color = tuple(unit_config['color'])
        self.description = unit_config['description']
        
        # Turn state
        self.has_moved = False
        self.has_attacked = False
    
    def is_alive(self):
        return self.current_hp > 0
    
    def can_move(self):
        return not self.has_moved and self.is_alive()
    
    def can_attack(self):
        return not self.has_attacked and self.is_alive()
    
    def move(self):
        self.has_moved = True
    
    def attack(self, target):
        if self.can_attack() and self.is_in_range(target):
            target.take_damage(self.strength)
            self.has_attacked = True
            return True
        return False
    
    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0
    
    def is_in_range(self, target):
        # Calculate Manhattan distance
        distance = abs(self.x - target.x) + abs(self.y - target.y)
        return distance <= self.range
    
    def reset_turn(self):
        self.has_moved = False
        self.has_attacked = False
    
    def get_info(self):
        return {
            'type': self.unit_type,
            'hp': f"{self.current_hp}/{self.max_hp}",
            'strength': self.strength,
            'range': self.range,
            'move': self.move_range,
            'description': self.description,
            'status': "Player" if self.is_player else "Enemy"
        }
    
    def get_move_range_cells(self, grid):
        """Return a list of (x,y) coordinates within movement range."""
        cells = []
        # Use breadth-first search to find all cells within movement range
        visited = set([(self.x, self.y)])
        queue = [(self.x, self.y, 0)]  # (x, y, distance)
        
        while queue:
            x, y, dist = queue.pop(0)
            
            # If we've used all movement, don't explore further
            if dist >= self.move_range:
                continue
                
            # Check all adjacent cells
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                # Skip if out of bounds or already visited
                if not (0 <= nx < grid.width and 0 <= ny < grid.height) or (nx, ny) in visited:
                    continue
                    
                # Skip if cell has a unit
                cell = grid.get_cell(nx, ny)
                if cell and cell['unit'] is not None:
                    continue
                
                # Get terrain movement cost
                terrain = cell['terrain']
                move_cost = grid.terrain_types[terrain]['movement_cost']
                
                # If we can move to this cell within our move range
                if dist + move_cost <= self.move_range:
                    cells.append((nx, ny))
                    visited.add((nx, ny))
                    queue.append((nx, ny, dist + move_cost))
        
        return cells
    
    def get_attack_range_cells(self, grid):
        """Return a list of (x,y) coordinates within attack range."""
        cells = []
        
        # Check all cells within attack range (Manhattan distance)
        for r in range(1, self.range + 1):
            for dx in range(-r, r + 1):
                dy_range = r - abs(dx)
                for dy in range(-dy_range, dy_range + 1):
                    nx, ny = self.x + dx, self.y + dy
                    
                    # Skip if out of bounds
                    if not (0 <= nx < grid.width and 0 <= ny < grid.height):
                        continue
                    
                    # Add to attack range cells
                    cells.append((nx, ny))
        
        return cells

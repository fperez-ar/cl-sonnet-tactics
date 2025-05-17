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
        self.max_move_points = unit_config['move']
        self.current_move_points = self.max_move_points  # Track remaining movement points
        self.color = tuple(unit_config['color'])
        self.description = unit_config['description']
        
        # Turn state
        self.has_moved = False  # Now indicates if unit moved at all this turn
        self.has_attacked = False
    
    def is_alive(self):
        return self.current_hp > 0
    
    def can_move(self):
        # Unit can move if it's alive and has movement points remaining
        return not self.has_attacked and self.current_move_points > 0 and self.is_alive()
    
    def move(self, movement_cost):
        # Update movement points when unit moves
        self.current_move_points -= movement_cost
        self.has_moved = True
        
        # If no movement points left, unit can't move again this turn
        if self.current_move_points <= 0:
            self.current_move_points = 0
    
    def can_attack(self):
        """Check if the unit can attack this turn."""
        return not self.has_attacked and self.is_alive()

    def attack(self, target):
        """Execute an attack on the target unit."""
        if self.can_attack() and self.is_in_range(target):
            # Calculate damage
            damage = self.strength
            
            # Apply damage to target
            target.take_damage(damage)
            
            # Mark unit as having attacked this turn
            self.has_attacked = True
            
            # After attacking, unit cannot move anymore this turn
            self.current_move_points = 0
            
            return True
        return False

    def is_in_range(self, target):
        """Check if target is within attack range."""
        # Calculate Manhattan distance
        distance = abs(self.x - target.x) + abs(self.y - target.y)
        return distance <= self.range

    def take_damage(self, damage):
        """Apply damage to this unit."""
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0
            
    def get_attack_range_cells(self, grid):
        """Return a list of (x,y) coordinates within attack range."""
        cells = []
        
        # Check all cells within attack range (Manhattan distance)
        for r in range(1, self.range + 1):
            for dx in range(-r, r + 1):
                # Calculate allowable dy values for this dx (to maintain Manhattan distance)
                dy_range = r - abs(dx)
                for dy in range(-dy_range, dy_range + 1):
                    nx, ny = self.x + dx, self.y + dy
                    
                    # Skip if out of bounds
                    if not (0 <= nx < grid.width and 0 <= ny < grid.height):
                        continue
                    
                    # Add to attack range cells
                    cells.append((nx, ny))
        
        return cells

    def get_valid_attack_targets(self, grid, enemy_units):
        """Return a list of enemy units that can be attacked."""
        targets = []
        attack_range_cells = self.get_attack_range_cells(grid)
        
        for enemy in enemy_units:
            if enemy.is_alive() and (enemy.x, enemy.y) in attack_range_cells:
                targets.append(enemy)
                
        return targets
    
    def reset_turn(self):
        self.has_moved = False
        self.has_attacked = False
        # Reset movement points at the start of a new turn
        self.current_move_points = self.max_move_points
    
    def get_info(self):
        return {
            'type': self.unit_type,
            'hp': f"{self.current_hp}/{self.max_hp}",
            'strength': self.strength,
            'range': self.range,
            'move': f"{self.current_move_points}/{self.max_move_points}",  # Show current/max move points
            'description': self.description,
            'status': "Player" if self.is_player else "Enemy"
        }
    
    def get_move_range_cells(self, grid):
        """Return a list of (x,y) coordinates within movement range based on remaining move points."""
        cells = []
        # Use breadth-first search with movement costs
        visited = {(self.x, self.y): 0}  # (x, y): movement_cost
        queue = [(self.x, self.y, 0)]  # (x, y, accumulated_cost)
        
        while queue:
            x, y, cost = queue.pop(0)
            
            # Don't add the unit's own position to the move range
            if (x, y) != (self.x, self.y):
                cells.append((x, y))
            
            # Check all adjacent cells
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                # Skip if out of bounds
                if not (0 <= nx < grid.width and 0 <= ny < grid.height):
                    continue
                    
                # Skip if cell has a unit
                cell = grid.get_cell(nx, ny)
                if cell and cell['unit'] is not None:
                    continue
                
                # Get terrain movement cost
                terrain = cell['terrain']
                move_cost = grid.terrain_types[terrain]['movement_cost']
                
                # Calculate the new total cost
                new_cost = cost + move_cost
                
                # If we can move to this cell within our remaining move points
                # and if this path is cheaper than any previously found path to this cell
                if (new_cost <= self.current_move_points and 
                    ((nx, ny) not in visited or new_cost < visited[(nx, ny)])):
                    visited[(nx, ny)] = new_cost
                    queue.append((nx, ny, new_cost))
        
        return cells
    
    def get_movement_cost_to(self, grid, target_x, target_y):
        """Calculate the movement cost to reach a specific cell."""
        # If target is the current position, cost is 0
        if target_x == self.x and target_y == self.y:
            return 0
            
        # Use Dijkstra's algorithm to find the shortest path
        import heapq
        
        # Priority queue of (cost, x, y)
        queue = [(0, self.x, self.y)]
        # Dictionary to store the shortest distance to each cell
        distances = {(self.x, self.y): 0}
        
        while queue:
            cost, x, y = heapq.heappop(queue)
            
            # If we reached the target, return the cost
            if x == target_x and y == target_y:
                return cost
                
            # If we've found a better path to this cell already, skip
            if cost > distances.get((x, y), float('inf')):
                continue
                
            # Check all adjacent cells
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                
                # Skip if out of bounds
                if not (0 <= nx < grid.width and 0 <= ny < grid.height):
                    continue
                    
                # Skip if cell has a unit (unless it's the target)
                cell = grid.get_cell(nx, ny)
                if cell and cell['unit'] is not None and (nx, ny) != (target_x, target_y):
                    continue
                
                # Get terrain movement cost
                terrain = cell['terrain']
                move_cost = grid.terrain_types[terrain]['movement_cost']
                
                # Calculate the new total cost
                new_cost = cost + move_cost
                
                # If this is a better path, update and add to queue
                if new_cost < distances.get((nx, ny), float('inf')):
                    distances[(nx, ny)] = new_cost
                    heapq.heappush(queue, (new_cost, nx, ny))
        
        # If we couldn't find a path, return infinity
        return float('inf')
    
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

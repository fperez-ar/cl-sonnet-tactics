# game_state.py
from unit import Unit
import random

class GameState:
    def __init__(self, grid, config, level_index=0):
        self.grid = grid
        self.config = config
        self.level_index = level_index
        self.units = []
        self.player_units = []
        self.enemy_units = []
        self.selected_unit = None
        self.cursor_x = 0
        self.cursor_y = 0
        self.current_turn = "player"  # "player" or "enemy"
        self.input_handler = None  # Will be set from main.py
        
        # Initialize units from level data
        self._initialize_units()
        self.combat_notifications = []

    def _initialize_units(self):
        """Initialize units based on level configuration."""
        # Clear existing units
        self.units = []
        self.player_units = []
        self.enemy_units = []
        
        # Retrieve unit position data from grid
        player_positions = self.grid.get_player_start_positions()
        enemy_positions = self.grid.get_enemy_start_positions()
        
        # Place player units from level configuration
        for unit_data in player_positions:
            if len(unit_data) >= 3:  # Ensure we have x, y, and unit_type
                x, y, unit_type = unit_data
                
                # Create unit with correct position and type
                unit = Unit(unit_type, True, self.config, x, y)
                self.units.append(unit)
                self.player_units.append(unit)
                
                # Place unit on grid
                self.grid.place_unit(unit, x, y)
                print(f"Placed player {unit_type} at ({x}, {y})")
            else:
                print(f"Warning: Invalid player unit data format: {unit_data}")
        
        # Place enemy units from level configuration
        for unit_data in enemy_positions:
            if len(unit_data) >= 3:  # Ensure we have x, y, and unit_type
                x, y, unit_type = unit_data
                
                # Create unit with correct position and type
                unit = Unit(unit_type, False, self.config, x, y)
                self.units.append(unit)
                self.enemy_units.append(unit)
                
                # Place unit on grid
                self.grid.place_unit(unit, x, y)
                print(f"Placed enemy {unit_type} at ({x}, {y})")
            else:
                print(f"Warning: Invalid enemy unit data format: {unit_data}")
    
    def update(self):
        # Check for victory conditions
        if not self.player_units:
            print("Game over: The enemy has won!")
            return
        
        if not self.enemy_units:
            print("Victory: You have defeated all enemies!")
            return
        
        # If it's the enemy's turn, let AI make moves
        if self.current_turn == "enemy":
            self._enemy_turn()

        self.combat_notifications = [n for n in self.combat_notifications if n.update()]
    
    def _enemy_turn(self):
        # Simple AI that moves and attacks
        for unit in self.enemy_units:
            if not unit.is_alive():
                continue
                
            # As long as the unit has movement points and hasn't attacked
            while unit.can_move() and unit.current_move_points > 0:
                # Find possible move targets within movement range based on current move points
                move_cells = unit.get_move_range_cells(self.grid)
                
                if move_cells:
                    # Choose a random move
                    new_x, new_y = random.choice(move_cells)
                    
                    # Calculate movement cost
                    movement_cost = unit.get_movement_cost_to(self.grid, new_x, new_y)
                    
                    # Skip if not enough movement points
                    if movement_cost > unit.current_move_points:
                        continue
                        
                    # Move the unit
                    self.grid.move_unit(unit.x, unit.y, new_x, new_y)
                    unit.move(movement_cost)
                else:
                    # No valid moves left
                    break
            
            # Try to attack if possible
            if unit.can_attack():
                # Find targets in range
                targets = []
                for player_unit in self.player_units:
                    if player_unit.is_alive() and unit.is_in_range(player_unit):
                        targets.append(player_unit)
                
                if targets:
                    # Attack a random target
                    target = random.choice(targets)
                    unit.attack(target)
                    
                    # Check if target was killed
                    if not target.is_alive():
                        self.player_units.remove(target)
                        
        # End the enemy turn
        self._end_turn()
    
    def select_unit_at_cursor(self):
        cell = self.grid.get_cell(self.cursor_x, self.cursor_y)
        if cell and cell['unit'] and cell['unit'].is_player:
            self.selected_unit = cell['unit']
            return True
        return False
    
    def move_selected_unit(self, to_x, to_y):
        """Move the selected unit to the specified coordinates if valid."""
        if not self.selected_unit or not self.selected_unit.can_move():
            return False
            
        # Check if the move is within the unit's move range
        move_cells = self.selected_unit.get_move_range_cells(self.grid)
        if (to_x, to_y) in move_cells:
            # Calculate the movement cost
            movement_cost = self.selected_unit.get_movement_cost_to(self.grid, to_x, to_y)
            
            # Check if unit has enough movement points
            if movement_cost > self.selected_unit.current_move_points:
                print(f"Not enough movement points. Cost: {movement_cost}, Available: {self.selected_unit.current_move_points}")
                return False
                
            from_x, from_y = self.selected_unit.x, self.selected_unit.y
            if self.grid.move_unit(from_x, from_y, to_x, to_y):
                # Reduce movement points by the cost
                self.selected_unit.move(movement_cost)
                print(f"Unit moved to {to_x}, {to_y}. Remaining move points: {self.selected_unit.current_move_points}")
                return True
        return False

    def attack_with_selected_unit(self, target_x, target_y):
        """Attack an enemy at the target coordinates."""
        if not self.selected_unit or not self.selected_unit.can_attack():
            return False
            
        # Get the target cell
        cell = self.grid.get_cell(target_x, target_y)
        if not cell or not cell['unit']:
            return False
            
        # Check if target is an enemy unit
        target = cell['unit']
        if target.is_player == self.selected_unit.is_player:
            return False
        
        # Attempt the attack
        if self.selected_unit.attack(target):
            # Log the attack
            print(f"{self.selected_unit.unit_type} attacked {target.unit_type} for {self.selected_unit.strength} damage")
            
            # Check if target was killed
            if not target.is_alive():
                print(f"{target.unit_type} was defeated!")
                if target in self.enemy_units:
                    self.enemy_units.remove(target)
                elif target in self.player_units:
                    self.player_units.remove(target)
                    
                # Remove the defeated unit from the grid
                self.grid.remove_unit(target.x, target.y)
            
            return True
        
        return False

    def get_attackable_enemies(self):
        """Return a list of enemy units that can be attacked by the selected unit."""
        if not self.selected_unit or not self.selected_unit.can_attack():
            return []
        
        return self.selected_unit.get_valid_attack_targets(self.grid, self.enemy_units)

    def get_attack_range_cells(self):
        """Return cells within attack range of selected unit."""
        if not self.selected_unit or not self.selected_unit.can_attack():
            return []
        return self.selected_unit.get_attack_range_cells(self.grid)    
    def end_player_turn(self):
        if self.current_turn == "player":
            self._end_turn()
            return True
        return False
    
    def _end_turn(self):
        if self.current_turn == "player":
            # Switch to enemy turn
            self.current_turn = "enemy"
        else:
            # Switch to player turn and reset all units
            self.current_turn = "player"
            for unit in self.units:
                if unit.is_alive():
                    unit.reset_turn()
        
        # Deselect unit when turn ends
        self.selected_unit = None
    
    def get_cursor_info(self):
        info = {}
        
        # Get terrain info
        terrain_info = self.grid.get_terrain_info(self.cursor_x, self.cursor_y)
        if terrain_info:
            info['terrain'] = terrain_info
        
        # Get unit info
        cell = self.grid.get_cell(self.cursor_x, self.cursor_y)
        if cell and cell['unit']:
            info['unit'] = cell['unit'].get_info()
        
        return info
    
    def get_move_range_cells(self):
        """Return cells within move range of selected unit."""
        if not self.selected_unit or not self.selected_unit.can_move():
            return []
        return self.selected_unit.get_move_range_cells(self.grid)
    
    def get_attack_range_cells(self):
        """Return cells within attack range of selected unit."""
        if not self.selected_unit or not self.selected_unit.can_attack():
            return []
        return self.selected_unit.get_attack_range_cells(self.grid)

    # Add this method to GameState
    def add_combat_notification(self, message, x, y, color=(255, 255, 255)):
        """Add a temporary combat notification."""
        notification = CombatNotification(message, x, y, color)
        self.combat_notifications.append(notification)
# game_state.py
from unit import Unit
import random

class GameState:
    def __init__(self, grid, config):
        self.grid = grid
        self.config = config
        self.units = []
        self.player_units = []
        self.enemy_units = []
        self.selected_unit = None
        self.cursor_x = 0
        self.cursor_y = 0
        self.current_turn = "player"  # "player" or "enemy"
        self.input_handler = None  # Will be set from main.py
        
        # Initialize units
        self._initialize_units()
    
    def _initialize_units(self):
        # Place some player units
        for i in range(3):
            unit_type = "melee" if i % 2 == 0 else "ranged"
            unit = Unit(unit_type, True, self.config, i, 0)
            self.units.append(unit)
            self.player_units.append(unit)
            self.grid.place_unit(unit, i, 0)
        
        # Place some enemy units
        for i in range(3):
            unit_type = "ranged" if i % 2 == 0 else "melee"
            unit = Unit(unit_type, False, self.config, i, self.grid.height - 1)
            self.units.append(unit)
            self.enemy_units.append(unit)
            self.grid.place_unit(unit, i, self.grid.height - 1)
    
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
    
    def _enemy_turn(self):
        # Simple AI that moves and attacks randomly
        for unit in self.enemy_units:
            if not unit.is_alive():
                continue
                
            if unit.can_move():
                # Find possible move targets within movement range
                move_cells = unit.get_move_range_cells(self.grid)
                
                if move_cells:
                    # Choose a random move
                    new_x, new_y = random.choice(move_cells)
                    self.grid.move_unit(unit.x, unit.y, new_x, new_y)
                    unit.move()
            
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
            from_x, from_y = self.selected_unit.x, self.selected_unit.y
            if self.grid.move_unit(from_x, from_y, to_x, to_y):
                self.selected_unit.move()
                return True
        return False

    
    def attack_with_selected_unit(self, target_x, target_y):
        if not self.selected_unit or not self.selected_unit.can_attack():
            return False
            
        cell = self.grid.get_cell(target_x, target_y)
        if cell and cell['unit'] and not cell['unit'].is_player:
            target = cell['unit']
            if self.selected_unit.attack(target):
                # Check if target was killed
                if not target.is_alive():
                    self.enemy_units.remove(target)
                return True
        return False
    
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

# renderer.py
import pygame

class Renderer:
    def __init__(self, screen, game_state, config):
        self.screen = screen
        self.game_state = game_state
        self.config = config
        self.font = pygame.font.SysFont(None, 24)
        
        # Colors
        self.colors = {
            'background': (0, 0, 0),
            'grid_line': (50, 50, 50),
            'cursor': (255, 255, 0),
            'info_panel': (30, 30, 30),
            'text': (255, 255, 255),
            'move_range': tuple(self.config['highlights']['move_range']),
            'attack_range': tuple(self.config['highlights']['attack_range'])
        }
    
    def render(self):
        self.screen.fill(self.colors['background'])
        
        # Render grid
        self._render_grid()
        
        # Render move and attack ranges for selected unit
        if self.game_state.selected_unit:
            self._render_move_range()
            self._render_attack_range()
        
        # Render units
        self._render_units()
        
        # Render cursor
        self._render_cursor()
        
        # Render info panels
        self._render_info_panels()
        
        # Update display
        pygame.display.flip()
    
    def _render_grid(self):
        cell_size = self.game_state.grid.cell_size
        
        # Draw terrain
        for y in range(self.game_state.grid.height):
            for x in range(self.game_state.grid.width):
                cell = self.game_state.grid.get_cell(x, y)
                terrain = cell['terrain']
                color = tuple(self.config['terrain_types'][terrain]['color'])
                
                rect = pygame.Rect(
                    x * cell_size, 
                    y * cell_size, 
                    cell_size, 
                    cell_size
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, self.colors['grid_line'], rect, 1)
    
    def _render_move_range(self):
        cell_size = self.game_state.grid.cell_size
        move_cells = self.game_state.get_move_range_cells()
        
        # Create a surface with alpha for move range
        move_highlight = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
        move_highlight.fill(self.colors['move_range'])
        
        for x, y in move_cells:
            self.screen.blit(move_highlight, (x * cell_size, y * cell_size))
    
    def _render_attack_range(self):
        cell_size = self.game_state.grid.cell_size
        attack_cells = self.game_state.get_attack_range_cells()
        
        # Create a surface with alpha for attack range
        attack_highlight = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
        attack_highlight.fill(self.colors['attack_range'])
        
        for x, y in attack_cells:
            self.screen.blit(attack_highlight, (x * cell_size, y * cell_size))
    
    def _render_units(self):
        cell_size = self.game_state.grid.cell_size
        
        for unit in self.game_state.units:
            if not unit.is_alive():
                continue
                
            # Draw circle for unit
            x_center = unit.x * cell_size + cell_size // 2
            y_center = unit.y * cell_size + cell_size // 2
            radius = cell_size // 3
            
            # Use unit's own color
            color = unit.color
            
            # If unit is selected, highlight it
            if unit == self.game_state.selected_unit:
                pygame.draw.circle(self.screen, (0, 255, 0), (x_center, y_center), radius + 3)
            
            pygame.draw.circle(self.screen, color, (x_center, y_center), radius)
            
            # Draw HP
            hp_text = self.font.render(str(unit.current_hp), True, self.colors['text'])
            self.screen.blit(hp_text, (x_center - 5, y_center - 8))
    
    def _render_cursor(self):
        cell_size = self.game_state.grid.cell_size
        x = self.game_state.cursor_x * cell_size
        y = self.game_state.cursor_y * cell_size
        
        rect = pygame.Rect(x, y, cell_size, cell_size)
        pygame.draw.rect(self.screen, self.colors['cursor'], rect, 3)
    
    def _render_info_panels(self):
        screen_width = self.config['game']['window']['width']
        screen_height = self.config['game']['window']['height']
        
        # Draw terrain info panel (lower right)
        terrain_panel = pygame.Rect(
            screen_width - 250, 
            screen_height - 100, 
            250, 
            100
        )
        pygame.draw.rect(self.screen, self.colors['info_panel'], terrain_panel)
        
        # Get and display cursor info
        cursor_info = self.game_state.get_cursor_info()
        
        # Render terrain info
        if 'terrain' in cursor_info:
            terrain = cursor_info['terrain']
            terrain_text = f"Terrain: {terrain['name']}"
            terrain_desc = f"Desc: {terrain['description']}"
            terrain_cost = f"Move Cost: {terrain['movement_cost']}"
            
            texts = [
                self.font.render(terrain_text, True, self.colors['text']),
                self.font.render(terrain_desc, True, self.colors['text']),
                self.font.render(terrain_cost, True, self.colors['text'])
            ]
            
            for i, text in enumerate(texts):
                self.screen.blit(text, (screen_width - 240, screen_height - 90 + i*25))
        
        # Draw unit info panel (lower left)
        if 'unit' in cursor_info:
            unit_panel = pygame.Rect(
                0,
                screen_height - 120,  # Increased height for move stat
                250,
                120
            )
            pygame.draw.rect(self.screen, self.colors['info_panel'], unit_panel)
            
            # Render unit info
            unit = cursor_info['unit']
            unit_text = f"Unit: {unit['type']} ({unit['status']})"
            unit_hp = f"HP: {unit['hp']}"
            unit_stats = f"STR: {unit['strength']} Range: {unit['range']}"
            unit_move = f"Move: {unit['move']}"  # Added move stat
            
            texts = [
                self.font.render(unit_text, True, self.colors['text']),
                self.font.render(unit_hp, True, self.colors['text']),
                self.font.render(unit_stats, True, self.colors['text']),
                self.font.render(unit_move, True, self.colors['text'])
            ]
            
            for i, text in enumerate(texts):
                self.screen.blit(text, (10, screen_height - 110 + i*25))
            
            # If this is a player unit, show order panel
            if 'status' in unit and unit['status'] == "Player":
                order_panel = pygame.Rect(
                    0,
                    screen_height - 170,
                    250,
                    50
                )
                pygame.draw.rect(self.screen, self.colors['info_panel'], order_panel)
                
                # Render order options
                orders_text = "[M] Move  [A] Attack  [P] Pass Turn"
                orders = self.font.render(orders_text, True, self.colors['text'])
                self.screen.blit(orders, (10, screen_height - 160))
        
        # Show current turn info
        turn_text = f"Current Turn: {self.game_state.current_turn.capitalize()}"
        turn_surface = self.font.render(turn_text, True, self.colors['text'])
        self.screen.blit(turn_surface, (screen_width // 2 - 80, 10))
        
        # Show current action mode
        if self.game_state.current_turn == "player":
            mode_text = f"Mode: {self.game_state.input_handler.action_mode.capitalize()}"
            mode_surface = self.font.render(mode_text, True, self.colors['text'])
            self.screen.blit(mode_surface, (screen_width // 2 - 50, 40))

# input_handler.py
import pygame

class InputHandler:
    def __init__(self, game_state, config):
        self.game_state = game_state
        self.config = config
        # Action mode is now only used for display purposes
        self.action_mode = "select"
        
        # Initialize key mappings from config
        self.key_map = self._initialize_key_map()
    
    def _initialize_key_map(self):
        key_map = {}
        
        # Map string key names to pygame key constants
        key_constants = {
            # Arrow keys
            "UP": pygame.K_UP,
            "DOWN": pygame.K_DOWN,
            "LEFT": pygame.K_LEFT,
            "RIGHT": pygame.K_RIGHT,
            
            # Letter keys
            "a": pygame.K_a, "b": pygame.K_b, "c": pygame.K_c, "d": pygame.K_d,
            "e": pygame.K_e, "f": pygame.K_f, "g": pygame.K_g, "h": pygame.K_h,
            "i": pygame.K_i, "j": pygame.K_j, "k": pygame.K_k, "l": pygame.K_l,
            "m": pygame.K_m, "n": pygame.K_n, "o": pygame.K_o, "p": pygame.K_p,
            "q": pygame.K_q, "r": pygame.K_r, "s": pygame.K_s, "t": pygame.K_t,
            "u": pygame.K_u, "v": pygame.K_v, "w": pygame.K_w, "x": pygame.K_x,
            "y": pygame.K_y, "z": pygame.K_z,
            
            # Number keys
            "0": pygame.K_0, "1": pygame.K_1, "2": pygame.K_2, "3": pygame.K_3,
            "4": pygame.K_4, "5": pygame.K_5, "6": pygame.K_6, "7": pygame.K_7,
            "8": pygame.K_8, "9": pygame.K_9,
            
            # Special keys
            "SPACE": pygame.K_SPACE,
            "RETURN": pygame.K_RETURN,
            "ESCAPE": pygame.K_ESCAPE,
            "TAB": pygame.K_TAB,
            "BACKSPACE": pygame.K_BACKSPACE,
            "SHIFT": pygame.K_LSHIFT,
            "CTRL": pygame.K_LCTRL,
            "ALT": pygame.K_LALT,
        }
        
        # Map action names to pygame key constants using config
        controls = self.config["controls"]
        
        key_map["cursor_up"] = key_constants.get(controls["cursor_up"], pygame.K_UP)
        key_map["cursor_down"] = key_constants.get(controls["cursor_down"], pygame.K_DOWN)
        key_map["cursor_left"] = key_constants.get(controls["cursor_left"], pygame.K_LEFT)
        key_map["cursor_right"] = key_constants.get(controls["cursor_right"], pygame.K_RIGHT)
        key_map["select_action"] = key_constants.get(controls["select_action"], pygame.K_SPACE)
        key_map["move_action"] = key_constants.get(controls["move_action"], pygame.K_m)
        key_map["attack_action"] = key_constants.get(controls["attack_action"], pygame.K_a)
        key_map["pass_turn"] = key_constants.get(controls["pass_turn"], pygame.K_p)
        
        return key_map
    
    def handle_event(self, event):
        if self.game_state.current_turn != "player":
            return  # Only process input during player's turn
            
        if event.type == pygame.KEYDOWN:
            # Movement keys for cursor
            if event.key == self.key_map["cursor_up"]:
                self.game_state.cursor_y = max(0, self.game_state.cursor_y - 1)
            elif event.key == self.key_map["cursor_down"]:
                self.game_state.cursor_y = min(self.game_state.grid.height - 1, self.game_state.cursor_y + 1)
            elif event.key == self.key_map["cursor_left"]:
                self.game_state.cursor_x = max(0, self.game_state.cursor_x - 1)
            elif event.key == self.key_map["cursor_right"]:
                self.game_state.cursor_x = min(self.game_state.grid.width - 1, self.game_state.cursor_x + 1)
            
            # Select unit action
            elif event.key == self.key_map["select_action"]:
                # Try to select a unit at the cursor position
                if self.game_state.select_unit_at_cursor():
                    print("Unit selected")
                    self.action_mode = "select"
                # If no unit selected, or if we have a unit and we're clicking on empty space, deselect
                elif self.game_state.selected_unit:
                    self.game_state.selected_unit = None
                    self.action_mode = "select"
                    print("Unit deselected")
                
            # Move action - immediately attempt to move to cursor position
            elif event.key == self.key_map["move_action"] and self.game_state.selected_unit:
                # Only set mode for display purposes
                self.action_mode = "move"
                
                # If cursor is at same position as unit, do nothing
                if (self.game_state.cursor_x == self.game_state.selected_unit.x and 
                    self.game_state.cursor_y == self.game_state.selected_unit.y):
                    print("Unit already at cursor position")
                    return
                
                # Get all valid move cells
                move_cells = self.game_state.selected_unit.get_move_range_cells(self.game_state.grid)
                
                # Check if cursor is on a valid move cell
                if (self.game_state.cursor_x, self.game_state.cursor_y) in move_cells:
                    # Calculate the movement delta
                    from_x, from_y = self.game_state.selected_unit.x, self.game_state.selected_unit.y
                    to_x, to_y = self.game_state.cursor_x, self.game_state.cursor_y
                    
                    # Attempt the move
                    if self.game_state.grid.move_unit(from_x, from_y, to_x, to_y):
                        self.game_state.selected_unit.move()
                        print(f"Unit moved to {to_x}, {to_y}")
                    else:
                        print("Move failed")
                else:
                    print("Cannot move to that location")
            
            # Attack action - immediately attempt to attack at cursor position
            elif event.key == self.key_map["attack_action"] and self.game_state.selected_unit:
                # Only set mode for display purposes
                self.action_mode = "attack"
                
                # Attempt to attack the unit at cursor position
                if self.game_state.attack_with_selected_unit(self.game_state.cursor_x, self.game_state.cursor_y):
                    print("Attack successful")
                else:
                    print("Cannot attack that target")
            
            # End turn
            elif event.key == self.key_map["pass_turn"]:
                if self.game_state.end_player_turn():
                    self.action_mode = "select"
                    print("Turn passed")

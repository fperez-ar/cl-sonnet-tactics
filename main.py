# main.py
import pygame
import yaml
import sys
from grid import Grid
from game_state import GameState
from input_handler import InputHandler
from renderer import Renderer

def load_config(config_file='config.yaml'):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def main():
    # Load configuration
    config = load_config()
    
    # Initialize pygame
    pygame.init()
    screen_width = config['game']['window']['width']
    screen_height = config['game']['window']['height']
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(config['game']['title'])
    
    # Create game components
    grid = Grid(config)
    game_state = GameState(grid, config)
    input_handler = InputHandler(game_state, config)  # Pass config here
    game_state.input_handler = input_handler  # Set input handler reference
    renderer = Renderer(screen, game_state, config)
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            input_handler.handle_event(event)
        
        # Update game state
        game_state.update()
        
        # Render the game
        renderer.render()
        
        # Cap the frame rate
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()

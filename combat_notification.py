# combat_notification.py
class CombatNotification:
    def __init__(self, message, x, y, color=(255, 255, 255), duration=60):
        self.message = message
        self.x = x
        self.y = y
        self.color = color
        self.duration = duration
        self.frames_left = duration
        self.y_offset = 0
    
    def update(self):
        self.frames_left -= 1
        # Float upward as the notification ages
        self.y_offset -= 0.5
        return self.frames_left > 0
    
    def render(self, screen, font):
        alpha = min(255, int(255 * (self.frames_left / self.duration)))
        text_surface = font.render(self.message, True, self.color)
        
        # Create a surface with alpha for fading
        temp_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))  # Transparent background
        temp_surface.blit(text_surface, (0, 0))
        
        # Apply alpha
        temp_surface.set_alpha(alpha)
        
        # Draw at position with current offset
        screen.blit(temp_surface, (self.x, self.y + self.y_offset))

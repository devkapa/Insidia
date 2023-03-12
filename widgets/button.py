import pygame
import os
from commons import render_text, BACKGROUND_COLOUR, get_current_path


pygame.mixer.init()

# RGB colour constants
DARK_GREY = (100, 100, 100)
WHITE = (255, 255, 255)
BLACK = (50, 50, 50)


# Fill all pixels of the surface with color, preserve transparency.
def fill(surface, color):
    width, height = surface.get_size()
    r, g, b = color
    for x in range(width):
        for y in range(height):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pygame.Color(r, g, b, a))


class Button:
    """
    The button structure allows for event-based interactive button logic in pygame.
    Allows for a text and image label with hover logic to improve user experience.
    """
    icon: pygame.Surface
    size: tuple
    mode: int
    last_surface: pygame.Surface | None
    hovering: bool

    CLICK_CHANNEL = pygame.mixer.Channel(1)
    CLICK_SOUND = pygame.mixer.Sound(os.path.join(get_current_path(), 'assets', 'sounds', 'click.mp3'))

    # Initialise the Button as a barebones structure to be later drawn. Prepare image icon
    def __init__(self, icon, size, event, mode, label, background_colour=BACKGROUND_COLOUR) -> None:
        self.rect = None
        self.pos = None
        self.icon = pygame.transform.scale(pygame.image.load(
            icon).convert_alpha(), (size[0] - 10, size[1] - 10))
        fill(self.icon, WHITE)
        self.size = size
        self.event = pygame.event.Event(event)
        self.mode = mode
        self.hovering = False
        self.label = label
        self.last_surface = None
        self.background_colour = background_colour

    # The method called to post the buttons event when it is clicked
    def on_click(self) -> bool:
        if self.last_surface.get_rect(topleft=self.pos).collidepoint(pygame.mouse.get_pos()):
            # Play click sound for accessibility
            if not self.CLICK_CHANNEL.get_busy():
                self.CLICK_CHANNEL.play(self.CLICK_SOUND)
            pygame.event.post(self.event)
            return True
        return False

    # The method called when the button is hovered
    def on_hover(self) -> bool:
        if self.last_surface.get_rect(topleft=self.pos).collidepoint(pygame.mouse.get_pos()):
            self.hovering = True
        else:
            self.hovering = False
        return self.hovering

    # Given a surface, draw on it the button and image or text label respective to hover status
    def create(self, surface, mode, left, top) -> None:

        # Cache current position
        self.pos = (left, top)
        
        # Prepare the surface everything will draw on
        button_surface = pygame.Surface(
            (self.size[0] + 2, self.size[1] + 2))
        button_surface.fill(self.background_colour)

        # Draw the main button rectangle and colour based on if it is hovered
        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1]) if not self.hovering else pygame.Rect(2, 2, self.size[0], self.size[1])
        shadow = pygame.Rect(2, 2, self.size[0], self.size[1])
        colour = BLACK if mode == self.mode or self.hovering else DARK_GREY
        pygame.draw.rect(button_surface, WHITE, shadow, border_radius=10)
        pygame.draw.rect(button_surface, colour, self.rect, border_radius=10)

        # Render the label if it is hovered, otherwise image icon
        if self.hovering:
            label = render_text(self.label, 20)
            button_surface.blit(
                label, ((self.size[0] / 2 - label.get_width() / 2) + 2, (self.size[1] / 2 - label.get_height() / 2) + 2))
        else:
            button_surface.blit(self.icon, ((
                                                self.size[0] / 2) - (self.icon.get_width() / 2),
                                            (self.size[1] / 2) - (self.icon.get_height() / 2)))
        
        # Cache the last known surface for efficiency
        self.last_surface = button_surface
        
        surface.blit(button_surface, (left, top))

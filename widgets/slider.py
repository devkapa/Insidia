import pygame
import math
from commons import render_text

# RGB colour constants
WHITE = (255, 255, 255)
BLACK = (80, 80, 80)
DARK_GREY = (100, 100, 100)
BACKGROUND_GREY = (239, 239, 239)


class Slider:
    """
    The textbox structure allows for a number to be selected within a certain minimum and maximum range. 
    It is a mouse-operated, interactive and easy to use interface to quickly select and change values.
    """
    minimum: int
    maximum: int
    default: int
    size_x: int
    size_y: int
    radius: int
    x_increment: float
    current_x: float
    current_surface: pygame.Surface | None
    pos: tuple | None
    clicked: bool
    tooltip: bool

    # Initialise the Slider as a barebones structure to be later drawn
    def __init__(self, minimum, maximum, size_x, size_y, radius, default=None, name="Slider") -> None:
        self.minimum = minimum
        self.maximum = maximum
        self.range_of_values = [i for i in range(self.minimum, self.maximum + 1)]
        self.size_x = size_x
        self.size_y = size_y
        self.radius = radius
        self.x_increment = self.size_x / (self.maximum - self.minimum)
        self.default = default
        self.reset()
        self.current_surface = None
        self.pos = None
        self.clicked = False
        self.tooltip = False
        self.name = render_text(name, 18, color=WHITE)

    # Calculate the currently selected value on the slider 
    def value(self) -> int:
        return self.range_of_values[math.floor((self.current_x - self.radius) / self.x_increment)]

    # Return if the slider surface has been clicked
    def get_clicked(self) -> bool:
        return self.clicked

    # Set if the slider surface has been clicked
    def set_clicked(self, clicked) -> None:
        self.clicked = clicked

    # Reset slider to the default value. If no default exists, set it to the minimum value.
    def reset(self) -> None:
        if self.default is None:
            self.current_x = self.radius
        else:
            try:
                value = [i for i in range(
                    self.minimum, self.maximum + 1)].index(self.default)
                self.current_x = self.radius + (value * self.x_increment)
            except ValueError:
                self.current_x = self.radius

    # Cache slider's current position when it is plotted 
    def set_pos(self, pos) -> None:
        self.pos = pos

    # Return the slider's last known position 
    def get_pos(self) -> tuple:
        return self.pos

    # Set the text to be displayed above the slider
    def set_tooltip(self, tooltip) -> None:
        self.tooltip = tooltip

    # Return the text to be displayed above the slider
    def get_tooltip(self) -> bool:
        return self.tooltip
    
    # Return a pygame Surface with the interactive slider
    def create(self) -> pygame.Surface:

        # Create transparent surface
        slider_surface = pygame.Surface(
            (self.size_x + self.radius * 2 + 50, self.size_y + self.radius + 50))
        slider_surface.set_colorkey((0, 0, 0))

        # Draw slider body and interactive circle
        slider_shadow = pygame.Rect(self.radius + 2, self.radius / 2 + 42, self.size_x, self.size_y)
        slider_body = pygame.Rect(self.radius, self.radius / 2 + 40, self.size_x, self.size_y)
        pygame.draw.rect(slider_surface, WHITE, slider_shadow, border_radius=5)
        pygame.draw.rect(slider_surface, DARK_GREY, slider_body, border_radius=5)
        pygame.draw.circle(slider_surface, BLACK,
                           (self.current_x + 2, self.size_y / 2 + self.radius / 2 + 42), self.radius + 1)
        pygame.draw.circle(slider_surface, WHITE,
                           (self.current_x, self.size_y / 2 + self.radius / 2 + 40), self.radius)
        
        # Draw the slider label above it
        slider_surface.blit(self.name, (0, 0))

        # If the tooltip must be displayed, draw it
        if self.get_tooltip():
            label = render_text(str(self.value()), 14, color=WHITE)
            label_background = (label.get_width() + 5, label.get_height() + 5)
            pygame.draw.rect(slider_surface, DARK_GREY,
                             pygame.Rect(self.current_x - (label_background[0] / 2), 0, label_background[0],
                                         label_background[1]), border_radius=2)
            slider_surface.blit(
                label, (self.current_x - label.get_width() / 2, 2.5))
        
        # Cache the last known surface for efficiency
        self.current_surface = slider_surface
        
        return slider_surface

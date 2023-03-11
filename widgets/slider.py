import pygame
import os
import math
import sys

# RGB colour constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (100, 100, 100)
BACKGROUND_GREY = (239, 239, 239)

# Font file names
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
    'Oxanium-Regular.ttf', 'press-start.ttf'

# Change current path if Insidia is running in an executable (.exe)
if getattr(sys, 'frozen', False):
    CurrentPath = sys._MEIPASS
else:
    CurrentPath = ''


def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    """Returns a pygame surface with the passed text in the app font."""
    font = pygame.font.Font(os.path.join(
        CurrentPath, 'assets', 'fonts', font), px)
    text = font.render(text, False, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


class Slider:
    """
    The textbox structure allows for a number to be selected within a certain minimum and maximum range. 
    It is a mouse-operated, interactive and easy to use interface to quickly select and change values.
    """
    min: int
    max: int
    default: int
    size_x: int
    size_y: int
    radius: int
    x_increment: int
    current_x: int
    current_surface: pygame.Surface | None
    pos: tuple | None
    clicked: bool
    tooltip: bool

    # Initialise the Slider as a barebones structure to be later drawn
    def __init__(self, min, max, size_x, size_y, radius, default=None, name="Slider") -> None:
        self.min = min
        self.max = max
        self.size_x = size_x
        self.size_y = size_y
        self.radius = radius
        self.x_increment = self.size_x / (self.max - self.min)
        self.default = default
        self.reset()
        self.current_surface = None
        self.pos = None
        self.clicked = False
        self.tooltip = False
        self.name = render_text(name, 18, color=WHITE)

    # Calculate the currently selected value on the slider 
    def value(self) -> int:
        return [i for i in range(self.min, self.max + 1)][math.floor((self.current_x - self.radius) / self.x_increment)]

    # Return if the slider surface has been clicked
    def get_clicked(self) -> bool:
        return self.clicked

    # Set if the slider surface has been clicked
    def set_clicked(self, bool) -> None:
        self.clicked = bool

    # Reset slider to the default value. If no default exists, set it to the minimum value.
    def reset(self) -> None:
        if self.default is None:
            self.current_x = self.radius
        else:
            try:
                value = [i for i in range(
                    self.min, self.max + 1)].index(self.default)
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
        pygame.draw.rect(slider_surface, DARK_GREY,
                         pygame.Rect(self.radius, self.radius / 2 + 40, self.size_x, self.size_y), border_radius=5)
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

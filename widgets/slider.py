import pygame
import os
import math


# RGB colour constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (100, 100, 100)
BACKGROUND_GREY = (239, 239, 239)

# Fonts
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
    'Oxanium-Regular.ttf', 'press-start.ttf'

# Returns a surface with text in the game font


def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    font = pygame.font.Font(os.path.join('assets', 'fonts', font), px)
    text = font.render(text, False, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


class Slider:

    min: int
    max: int
    size_x: int
    size_y: int
    radius: int
    x_increment: int
    current_x: int
    current_surface: pygame.Surface
    pos: tuple
    clicked: bool

    def __init__(self, min, max, size_x, size_y, radius) -> None:
        self.min = min
        self.max = max
        self.size_x = size_x
        self.size_y = size_y
        self.radius = radius
        self.x_increment = self.size_x / (self.max - self.min)
        self.current_x = self.radius
        self.current_surface = None
        self.pos = None
        self.clicked = False

    def value(self) -> int:
        return [i for i in range(self.min, self.max + 1)][math.floor((self.current_x - self.radius)/self.x_increment)]

    def get_clicked(self) -> bool:
        return self.clicked

    def set_clicked(self, bool) -> None:
        self.clicked = bool

    def move(self, val) -> None:
        if self.current_x + val < self.radius:
            self.current_x = self.radius
            return
        if self.current_x + val > self.radius + self.size_x:
            self.current_x = self.radius + self.size_x
            return
        self.current_x += val

    def set_pos(self, pos) -> None:
        self.pos = pos

    def get_pos(self) -> tuple:
        return self.pos

    def create(self) -> pygame.Surface:
        slider_surface = pygame.Surface(
            (self.size_x + self.radius*2 + 50, self.size_y + self.radius + 50))
        slider_surface.set_colorkey((0, 0, 0))
        pygame.draw.rect(slider_surface, DARK_GREY,
                         pygame.Rect(self.radius, self.radius/2 + 40, self.size_x, self.size_y))
        pygame.draw.circle(slider_surface, WHITE,
                           (self.current_x, self.size_y/2 + self.radius/2 + 40), self.radius)
        label = render_text(str(self.value()), 14, color=WHITE)
        label_background = (label.get_width() + 5, label.get_height() + 5)
        pygame.draw.rect(slider_surface, DARK_GREY,
                         pygame.Rect(self.current_x - (label_background[0]/2), 0, label_background[0], label_background[1]), border_radius=2)
        slider_surface.blit(
            label, (self.current_x - label.get_width()/2, 2.5))
        self.current_surface = slider_surface
        return slider_surface

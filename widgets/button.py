import pygame
import os
import sys

DARK_GREY = (100, 100, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOUR = (14, 17, 23)

# Fonts
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
    'Oxanium-Regular.ttf', 'press-start.ttf'

if getattr(sys, 'frozen', False):
    CurrentPath = sys._MEIPASS
else:
    CurrentPath = ''


def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    font = pygame.font.Font(os.path.join(
        CurrentPath, 'assets', 'fonts', font), px)
    text = font.render(text, False, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


# Fill all pixels of the surface with color, preserve transparency.
def fill(surface, color):
    width, height = surface.get_size()
    r, g, b = color
    for x in range(width):
        for y in range(height):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pygame.Color(r, g, b, a))


class Button:
    icon: pygame.Surface
    size: tuple
    mode: int
    last_surface: pygame.Surface
    hovering: bool

    def __init__(self, icon, size, event, mode, label) -> None:
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

    def on_click(self) -> None:
        if self.last_surface.get_rect(topleft=self.pos).collidepoint(pygame.mouse.get_pos()):
            pygame.event.post(self.event)

    def on_hover(self) -> bool:
        if self.last_surface.get_rect(topleft=self.pos).collidepoint(pygame.mouse.get_pos()):
            self.hovering = True
        else:
            self.hovering = False
        return self.hovering

    def create(self, surface, mode, left, top) -> None:
        self.pos = (left, top)
        label = render_text(self.label, 20)
        button_surface = pygame.Surface(
            (self.size[0], self.size[1]))
        button_surface.fill(BACKGROUND_COLOUR)
        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        colour = BLACK if mode == self.mode or self.hovering else DARK_GREY
        pygame.draw.rect(button_surface, colour, self.rect, border_radius=10)
        if self.hovering:
            button_surface.blit(
                label, (self.size[0] / 2 - label.get_width() / 2, self.size[1] / 2 - label.get_height() / 2))
        else:
            button_surface.blit(self.icon, ((
                                                self.size[0] / 2) - (self.icon.get_width() / 2),
                                            (self.size[1] / 2) - (self.icon.get_height() / 2)))
        self.last_surface = button_surface
        surface.blit(button_surface, (left, top))

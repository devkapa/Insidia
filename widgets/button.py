import pygame
import os


DARK_GREY = (100, 100, 100)
WHITE = (255, 255, 255)
BACKGROUND_COLOUR = (14, 17, 23)

# Fonts
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
    'Oxanium-Regular.ttf', 'press-start.ttf'


def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    font = pygame.font.Font(os.path.join('assets', 'fonts', font), px)
    text = font.render(text, False, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


class Button:

    icon: pygame.Surface
    size: tuple
    mode: int
    last_surface: pygame.Surface
    hovering: bool

    def __init__(self, icon, size, event, mode, label) -> None:
        self.icon = pygame.transform.scale(pygame.image.load(
            icon).convert_alpha(), (size[0], size[1]))
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
            (self.size[0], self.size[1] + label.get_height() + 10))
        button_surface.fill(BACKGROUND_COLOUR)
        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        colour = WHITE if mode == self.mode or self.hovering else DARK_GREY
        pygame.draw.rect(button_surface, colour, self.rect, border_radius=10)
        button_surface.blit(self.icon, (0, 0))
        if self.hovering:
            button_surface.blit(label, (0, self.size[1] + 10))
        self.last_surface = button_surface
        surface.blit(button_surface, (left, top))

import os
import sys
import pygame

WHITE = (255, 255, 255)
BACKGROUND_COLOUR = (14, 17, 23)

# Font file names
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
        'Oxanium-Regular.ttf', 'press-start.ttf'


# Change current path for main.py if Insidia is running in an executable (.exe)
def get_current_path_main():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return ''


# Change current path if Insidia is running in an executable (.exe)
def get_current_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(__file__)


def get_opus_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)


def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    """Returns a pygame surface with the passed text in the app font."""
    font = pygame.font.Font(os.path.join(get_current_path_main(), 'assets', 'fonts', font), px)
    text = font.render(text, True, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


def coloured_text(text, px, color=WHITE):
    """Returns text surface(s) that are coloured separately."""
    dummy_text = render_text(text, px)
    master_surface = pygame.Surface(dummy_text.get_size())
    master_surface.set_colorkey((0, 0, 0))
    text: str = text.split("||")
    current_colour = color
    x_accumulated = 0
    for split_section in text:
        if split_section.startswith("col."):
            current_colour = eval(split_section[4:])
            continue
        split_text = render_text(split_section, px, color=current_colour)
        master_surface.blit(split_text, (x_accumulated, 0))
        x_accumulated += split_text.get_width()
    return master_surface


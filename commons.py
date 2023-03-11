import os
import sys
import pygame

WHITE = (255, 255, 255)

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


def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    """Returns a pygame surface with the passed text in the app font."""
    font = pygame.font.Font(os.path.join(get_current_path_main(), 'assets', 'fonts', font), px)
    text = font.render(text, True, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text

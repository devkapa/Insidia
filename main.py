import os
import sys

import pygame
import requests
from pygame.locals import *

version = "alpha-0.1"
# github_url = "https://api.github.com/repos/devkapa/InsidiaDiff/releases/latest"

# Enable double buffer
flags = DOUBLEBUF

# Initialise pygame modules
pygame.font.init()
pygame.display.init()

# RGB colour constants
WHITE = (255, 255, 255)
YELLOW = (253, 248, 140)
AQUA = (0, 255, 255)
PINK = (255, 225, 225)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (168, 168, 168)
BLACK = (0, 0, 0)
BACKGROUND_COLOUR = (14, 17, 23)
SIDEBAR_COLOUR = (38, 39, 48)

# Size constants
WIDTH, HEIGHT = 1000, 800
SIDEBAR_WIDTH, SIDEBAR_HEIGHT = 250, HEIGHT
SIDEBAR_PADDING = 10

# Create an opaque window surface with defined width and height, and set a title
WIN = pygame.display.set_mode((WIDTH, HEIGHT), flags, 8)
WIN.set_alpha(None)
pygame.display.set_caption("Insidia")

# Set the icon of the window
ICON = pygame.image.load(os.path.join('assets', 'textures', 'logo.png'))
pygame.display.set_icon(ICON)

# Frames per second constant
FPS = 60

# Fonts
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
    'Oxanium-Regular.ttf', 'press-start.ttf'

# Enum values for code readability
HOME, SCIENTIFIC, GRAPHING, SETTINGS = 0, 1, 2, 3
RETRACTED, EXTENDED = 0, 1


# Returns a surface with text in the game font
def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    font = pygame.font.Font(os.path.join('assets', 'fonts', font), px)
    text = font.render(text, True, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


def get_sidebar(sidebar):
    if sidebar == EXTENDED:
        sidebar_surface = pygame.Surface((SIDEBAR_WIDTH, SIDEBAR_HEIGHT))
        sidebar_surface.fill(SIDEBAR_COLOUR)
        close_button = pygame.Rect(SIDEBAR_WIDTH - 30 - SIDEBAR_PADDING, SIDEBAR_PADDING, 30, 30)
        close_text = render_text("X", 35 if close_button.collidepoint(pygame.mouse.get_pos()) else 30, font=TITLE)
        sidebar_surface.blit(close_text, (SIDEBAR_WIDTH - close_text.get_width() - SIDEBAR_PADDING, SIDEBAR_PADDING))
        return sidebar_surface, close_button

    if sidebar == RETRACTED:
        sidebar_surface = pygame.Surface((50, 50))
        sidebar_surface = sidebar_surface.convert_alpha()
        sidebar_surface.fill((0, 0, 0, 0))
        open_button = pygame.Rect(SIDEBAR_PADDING, SIDEBAR_PADDING, 30, 30)
        open_text = render_text("»", 35 if open_button.collidepoint(pygame.mouse.get_pos()) else 30, font=TITLE)
        sidebar_surface.blit(open_text, (SIDEBAR_PADDING, SIDEBAR_PADDING))
        return sidebar_surface, open_button


def draw_home():
    WIN.fill(BACKGROUND_COLOUR)


def main():
    # Initialise pygame's clock and start the game loop
    clock = pygame.time.Clock()
    running = True

    # Set the initial state to the title screen
    state = HOME
    # update_message = ""

    # Set the sidebar to default open
    sidebar_state = EXTENDED
    sidebar_anim_frames = 0

    # Check for updates from GitHub - if this version doesn't match the latest version
    # If there is no internet, print error but run program
    # try:
    #    response = requests.get(github_url, timeout=3)
    #    if response.json()["tag_name"] != version:
    #        update_message = "There is a new version available! Click here to download."
    # except requests.ConnectionError:
    #    update_message = "Cannot check for updates."
    # except requests.Timeout:
    #    update_message = "Cannot check for updates."

    while running:

        # Limit the loop to run only 60 times per second
        clock.tick(FPS)

        # Get sidebar surface and button rects
        sidebar = get_sidebar(sidebar_state)

        # Iterate through pygame events
        for event in pygame.event.get():

            # Exit the program if the user quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Check if the user clicked the mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Close the sidebar if "X" pressed
                if sidebar[1].collidepoint(event.pos):
                    if sidebar_state == EXTENDED:
                        sidebar_state = RETRACTED
                    else:
                        sidebar_state = EXTENDED
                        sidebar_anim_frames = SIDEBAR_WIDTH

            if state == HOME:
                draw_home()

            if state == SCIENTIFIC:
                pass

            if state == GRAPHING:
                pass

            if state == SETTINGS:
                pass

        if sidebar_state == EXTENDED:
            WIN.blit(sidebar[0], (0 - sidebar_anim_frames, 0))
            sidebar_anim_frames -= 50 if 0 < sidebar_anim_frames else 0
        else:
            WIN.blit(sidebar[0], (0, 0))

        pygame.display.update()


if __name__ == '__main__':
    main()

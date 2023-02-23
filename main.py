import os
import sys
import requests

import pygame
from pygame.locals import *

from symengine import sympify, Eq, Symbol

from calc.graphing import Graph
from calc.relations import Relation


# Versioning
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
SIDEBAR_HIGHLIGHT = (58, 59, 70)

# Size constants
WIDTH, HEIGHT = 1200, 800
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
FPS = 120

# Fonts
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
    'Oxanium-Regular.ttf', 'press-start.ttf'

# Enum values for code readability
HOME, SCIENTIFIC, GRAPHING, SETTINGS = 0, 1, 2, 3
RETRACTED, EXTENDED = 0, 1
SIDEBAR_SURFACE, SIDEBAR_BUTTON, SIDEBAR_PAGES = 0, 1, 2


# Returns a surface with text in the game font
def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    font = pygame.font.Font(os.path.join('assets', 'fonts', font), px)
    text = font.render(text, True, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


# Create a sidebar depending on whether it is extended or not
def get_sidebar(sidebar, status):
    if sidebar == EXTENDED:

        # Sidebar background
        sidebar_surface = pygame.Surface((SIDEBAR_WIDTH, SIDEBAR_HEIGHT))
        sidebar_surface.fill(SIDEBAR_COLOUR)

        # Close button
        close_button = pygame.Rect(
            SIDEBAR_WIDTH - 30 - SIDEBAR_PADDING, SIDEBAR_PADDING, 30, 30)
        close_text = render_text("X", 35 if close_button.collidepoint(
            pygame.mouse.get_pos()) else 30, font=TITLE)
        sidebar_surface.blit(close_text, (SIDEBAR_WIDTH -
                             close_text.get_width() - SIDEBAR_PADDING, SIDEBAR_PADDING))

        # Pages
        pages = ["Home", "Scientific Calculator",
                 "Graphing Calculator", "Settings"]
        pygame.display.set_caption(f"{pages[status]} • Insidia")
        for index, page in enumerate(pages):
            page_button = pygame.Surface(
                (SIDEBAR_WIDTH - (SIDEBAR_PADDING*2), 30))
            page_rect = pygame.Rect(
                (SIDEBAR_PADDING, 100+(index*40)), (SIDEBAR_WIDTH - (SIDEBAR_PADDING*2), 30))
            page_button.fill(SIDEBAR_HIGHLIGHT if status == index or page_rect.collidepoint(
                pygame.mouse.get_pos()) else SIDEBAR_COLOUR)
            page_text = render_text(page, 20)
            page_button.blit(page_text, (SIDEBAR_PADDING, 5))
            sidebar_surface.blit(
                page_button, (SIDEBAR_PADDING, 100+(index*40)))
            pages[index] = page_rect

        # Page specific controls

        return sidebar_surface, close_button, pages

    if sidebar == RETRACTED:
        open_button = pygame.Rect(SIDEBAR_PADDING, SIDEBAR_PADDING, 30, 30)
        open_text = render_text("»", 35 if open_button.collidepoint(
            pygame.mouse.get_pos()) else 30, font=TITLE)
        return open_text, open_button


def draw_home(sidebar_offset, graph):
    WIN.fill(BACKGROUND_COLOUR)
    title = render_text("Insidia: Your partner in math", 40, font=TITLE)
    WIN.blit(title, (sidebar_offset + 80, 80))
    WIN.blit(graph.create((-15, 15), (-5, 5), [Relation(Eq(sympify("sin(x)"), sympify("y")), (26, 87, 176))], scale_x=graph.get_sliders()[0].value(), scale_y=graph.get_sliders()[1].value()),
             (sidebar_offset + 80, 190))
    graph.set_pos((sidebar_offset + 80, 190))
    accumulated = 0
    for slider in graph.get_sliders():
        surface = slider.create()
        WIN.blit(surface, (sidebar_offset + 700, 190 + (accumulated)))
        slider.set_pos((sidebar_offset + 700, 190 + (accumulated)))
        accumulated += surface.get_height() + 20


def draw_scientific():
    WIN.fill(BACKGROUND_COLOUR)


def draw_graphing():
    WIN.fill(BACKGROUND_COLOUR)


def draw_settings():
    WIN.fill(BACKGROUND_COLOUR)


def main():
    # Initialise pygame's clock and start the game loop
    clock = pygame.time.Clock()
    running = True

    # Set the initial state to the title screen
    current_state = HOME
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

    clicked = None

    graph = Graph("", (600, 300))

    while running:

        # Limit the loop to run only 60 times per second
        clock.tick(FPS)

        # Get sidebar surface and button rects
        sidebar = get_sidebar(sidebar_state, current_state)

        # Iterate through pygame events
        for event in pygame.event.get():

            # Exit the program if the user quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Check if the user clicked the mouse
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Change sidebar state if button is pressed
                if sidebar[SIDEBAR_BUTTON].collidepoint(event.pos):
                    if sidebar_state == EXTENDED:
                        sidebar_state = RETRACTED
                    else:
                        sidebar_state = EXTENDED
                        sidebar_anim_frames = SIDEBAR_WIDTH

                # Reload sidebar after state change
                sidebar = get_sidebar(sidebar_state, current_state)

                # Change program state if sidebar page button is pressed
                if len(sidebar) > SIDEBAR_PAGES:
                    for state in [HOME, SCIENTIFIC, GRAPHING, SETTINGS]:
                        if sidebar[SIDEBAR_PAGES][state].collidepoint(event.pos):
                            current_state = state

        if current_state == HOME:
            draw_home(230 if sidebar_state == EXTENDED else 0, graph)

            buttons_pressed = pygame.mouse.get_pressed(num_buttons=3)

            clicked = graph.handle_changes(buttons_pressed, clicked)

        if current_state == SCIENTIFIC:
            draw_scientific()

        if current_state == GRAPHING:
            draw_graphing()

        if current_state == SETTINGS:
            draw_settings()

        # Draw the sidebar onto the screen
        if sidebar_state == EXTENDED:
            WIN.blit(sidebar[SIDEBAR_SURFACE], (0 - sidebar_anim_frames, 0))
            sidebar_anim_frames -= 25 if 0 < sidebar_anim_frames else 0
        else:
            WIN.blit(sidebar[SIDEBAR_SURFACE], (10, 10))

        pygame.display.update()


if __name__ == '__main__':
    main()

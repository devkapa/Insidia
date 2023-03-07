import os
import sys

import pygame
from random import choice
from pygame.locals import *

from calc.graphing import Graph
from calc.relations import Relation

from widgets.textbox import Textbox
from tkinter import messagebox


# Versioning
version = "alpha-1.0"

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

if getattr(sys, 'frozen', False):
    CurrentPath = sys._MEIPASS
else:
    CurrentPath = os.path.dirname(__file__)

# Set the icon of the window
ICON = pygame.image.load(os.path.join(
    CurrentPath, 'assets', 'textures', 'logo.png'))
pygame.display.set_icon(ICON)
ICON_SPLASH = pygame.transform.scale(ICON, (400, 400))


# Fonts
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
    'Oxanium-Regular.ttf', 'press-start.ttf'


# Returns a surface with text in the game font
def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    font = pygame.font.Font(os.path.join(
        CurrentPath, 'assets', 'fonts', font), px)
    text = font.render(text, True, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


# Loading screen
LOAD_MESSAGES = ["Compiling infinite digits of pi... this could take a while.",
                 "Conjuring up a mathematical genie to do the calculations for us... Sit tight!",
                 "Summoning the spirits of ancient mathematicians... hope they're in a good mood.",
                 "Preparing to launch the world's largest abacus... hold on tight!",
                 "Setting up a team of calculator-toting chimpanzees... standby for results.",
                 "Spinning up the quantum calculator... it may take some time to stabilize.",
                 "Assembling a team of mathemagicians to tackle your calculations... Abracadabra!",
                 "Initiating the mathematical singularity... brace for impact!"]

init_text = render_text(choice(LOAD_MESSAGES), 30, font=TITLE)
WIN.blit(ICON_SPLASH, (WIDTH/2 - ICON_SPLASH.get_width() /
                       2, HEIGHT/2 - ICON_SPLASH.get_height()/2 - init_text.get_height()))
WIN.blit(init_text, (WIDTH/2 - init_text.get_width() /
                     2, HEIGHT/2 + ICON_SPLASH.get_height()/2 + 10))
pygame.display.update()

# Frames per second constant
FPS = 120

# Enum values for code readability
HOME, GRAPHING = 0, 1
RETRACTED, EXTENDED = 0, 1
SIDEBAR_SURFACE, SIDEBAR_BUTTON, SIDEBAR_PAGES = 0, 1, 2

SQUARE_WAVE = "y = (4/pi)*sin(pi*x)+(4/pi)*(1/3)*sin(3*pi*x)+(4/pi)*(1/5)*sin(5*pi*x)+(4/pi)*(1/7)*sin(7*pi*x)+(4/pi)*(1/9)*sin(9*pi*x)"
UGLY_CHAOS = "sin(cos(tan(x*y))) = sin(cos(tan(x)))"

home_rels = [Relation(SQUARE_WAVE, (168, 113, 255))]


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
        pages = ["Home", "Graphing Calculator"]
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
    WIN.blit(graph.create((-10, 10), (-2, 2), home_rels, (sidebar_offset + 80, 190), scale_x=graph.get_sliders()[0].value(), scale_y=graph.get_sliders()[1].value()),
             (sidebar_offset + 80, 190))
    graph.set_pos((sidebar_offset + 80, 190))
    y_accumulated = 0
    for slider in graph.get_sliders():
        surface = slider.create()
        WIN.blit(surface, (sidebar_offset + 700, 190 + y_accumulated))
        slider.set_pos((sidebar_offset + 700, 190 + y_accumulated))
        y_accumulated += surface.get_height() + 20
    x_accumulated = 0
    for button in graph.get_buttons():
        button.create(WIN, graph.get_mode(), sidebar_offset + 710 +
                      x_accumulated, 190 + y_accumulated)
        x_accumulated += button.size[0] + 15
    subtitle = render_text(
        "Math no longer has to be criminal. Visualise stunning, interactive graphs. Get started by exploring the sidebar.", 15)
    WIN.blit(subtitle, (sidebar_offset + 80, 530))


def draw_graphing(sidebar_offset, graph, rels, func_domain, func_range):
    WIN.fill(BACKGROUND_COLOUR)
    graph.set_pos((sidebar_offset + 70, 50))
    y_accumulated = 0
    for slider in graph.get_sliders():
        surface = slider.create()
        WIN.blit(surface, (sidebar_offset +
                 graph.size[0] + 90, 50 + y_accumulated))
        slider.set_pos(
            (sidebar_offset + graph.size[0] + 90, 50 + y_accumulated))
        y_accumulated += surface.get_height() + 20
    x_accumulated = 0
    for i, button in enumerate(graph.get_buttons()):
        if i != 3:
            button.create(WIN, graph.get_mode(), sidebar_offset + graph.size[0] + 100 +
                          x_accumulated, 50 + y_accumulated)
            if i < 2:
                x_accumulated += button.size[0] + 15
            continue
        button.create(WIN, graph.get_mode(), sidebar_offset + graph.size[0] + 100 +
                      x_accumulated + 5, 50 + y_accumulated + 80)
    y_accumulated += 70
    x_accumulated = 0
    for i, textbox in enumerate(graph.get_d_r_boxes()):
        textbox.create(WIN, sidebar_offset +
                       graph.size[0] + 100 + x_accumulated, 50 + y_accumulated)
        if i == 1:
            y_accumulated += 60
            x_accumulated -= textbox.size[0] + 15
            continue
        x_accumulated += textbox.size[0] + 15
    y_accumulated += 70
    for textbox in graph.get_textboxes():
        textbox.create(WIN, sidebar_offset +
                       graph.size[0] + 100, 50 + y_accumulated)
        y_accumulated += textbox.size[1] + 40
    WIN.blit(graph.create(func_domain, func_range, list(rels.values()), (sidebar_offset + 70, 50), scale_x=graph.get_sliders()[0].value(), scale_y=graph.get_sliders()[1].value()),
             (sidebar_offset + 70, 50))


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

    clicked = None

    demo_graph = Graph((600, 300))
    calc_graph = Graph((650, 700), equations=5, clear=True)

    rels = {}
    last_domain = (-10, 10)
    last_range = (-5, 5)

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

            if event.type == Graph.PAN_EVENT:
                demo_graph.set_mode(Graph.PAN)
                calc_graph.set_mode(Graph.PAN)

            if event.type == Graph.TOOLTIP_EVENT:
                demo_graph.set_mode(Graph.TOOLTIP)
                calc_graph.set_mode(Graph.TOOLTIP)

            if event.type == Graph.RESET_EVENT:
                demo_graph.reset()
                calc_graph.reset()

            if event.type == Graph.CLEAR_EVENT:
                for textbox in calc_graph.get_textboxes():
                    textbox.reset()
                for textbox in calc_graph.get_d_r_boxes():
                    textbox.value = textbox.default
                calc_graph.reset()

            if event.type == pygame.KEYDOWN:
                for textbox in calc_graph.get_textboxes():
                    if textbox.active:
                        if event.key == pygame.K_RETURN:
                            textbox.set_active(False)
                            try:
                                if textbox.get_text() != "":
                                    if textbox not in rels:
                                        rels[textbox] = Relation(
                                            textbox.get_text(), textbox.get_colour())
                                    else:
                                        if rels[textbox].get_original() != textbox.get_text():
                                            rels[textbox] = Relation(
                                                textbox.get_text(), textbox.get_colour())
                                    textbox.set_validity(True)
                                else:
                                    if textbox in rels:
                                        rels.pop(textbox)
                                    textbox.set_validity(True)
                            except:
                                messagebox.showerror(
                                    "Error", f"Thats an invalid expression.\n\"{textbox.get_text()}\"\nIf you are multiplying two terms (e.g. 2sin(x)), try adding a * between them. (2*sin(x))")
                                textbox.set_validity(False)
                                if textbox in rels:
                                    rels.pop(textbox)
                        elif event.key == pygame.K_BACKSPACE:
                            textbox.backspace()
                        elif event.key in Textbox.ARROWS:
                            textbox.move_cursor(event.key)
                        elif event.key in Textbox.WHITELIST:
                            textbox.add_text(event.unicode)
                for textbox in calc_graph.get_d_r_boxes():
                    if textbox.active:
                        if event.key == pygame.K_RETURN:
                            textbox.set_active(False)
                        elif event.key == pygame.K_BACKSPACE:
                            textbox.backspace()
                        elif event.key in Textbox.ARROWS:
                            textbox.move_cursor(event.key)
                        elif event.key in Textbox.WHITELIST:
                            textbox.add_text(event.unicode)

            # Check if the user clicked the mouse
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Change sidebar state if button is pressed
                if sidebar[SIDEBAR_BUTTON].collidepoint(event.pos):
                    if sidebar_state == EXTENDED:
                        sidebar_state = RETRACTED
                        calc_graph.extend(850)
                    else:
                        sidebar_state = EXTENDED
                        calc_graph.extend(650)
                        sidebar_anim_frames = SIDEBAR_WIDTH

                # Reload sidebar after state change
                sidebar = get_sidebar(sidebar_state, current_state)

                # Change program state if sidebar page button is pressed
                if len(sidebar) > SIDEBAR_PAGES:
                    for state in [HOME, GRAPHING]:
                        if sidebar[SIDEBAR_PAGES][state].collidepoint(event.pos):
                            current_state = state

        if current_state == HOME:
            draw_home(230 if sidebar_state == EXTENDED else 0, demo_graph)
            buttons_pressed = pygame.mouse.get_pressed(num_buttons=3)
            clicked = demo_graph.handle_changes(buttons_pressed, clicked)

        if current_state == GRAPHING:
            for textbox in calc_graph.get_textboxes():
                if not textbox.active:
                    try:
                        if textbox.get_text() != "":
                            if textbox not in rels:
                                rels[textbox] = Relation(
                                    textbox.get_text(), textbox.get_colour())
                            else:
                                if rels[textbox].get_original() != textbox.get_text():
                                    rels[textbox] = Relation(
                                        textbox.get_text(), textbox.get_colour())
                            textbox.set_validity(True)
                        else:
                            if textbox in rels:
                                rels.pop(textbox)
                            textbox.set_validity(True)
                    except:
                        textbox.set_validity(False)
                        if textbox in rels:
                            rels.pop(textbox)
            active = False
            for textbox in calc_graph.get_d_r_boxes():
                if textbox.active:
                    active = True
            if not active:
                x_min, x_max, y_min, y_max = calc_graph.get_d_r_boxes()
                try:
                    if int(x_min.get_text()) >= int(x_max.get_text()):
                        x_min.value = str(last_domain[0])
                        x_max.value = str(last_domain[1])
                        messagebox.showerror(
                            "Error", "Minimum X value must be less than the Maximum X.")
                    if int(y_min.get_text()) >= int(y_max.get_text()):
                        y_min.value = str(last_range[0])
                        y_max.value = str(last_range[1])
                        messagebox.showerror(
                            "Error", "Minimum Y value must be less than the Maximum Y.")
                    func_domain = (int(x_min.get_text()),
                                   int(x_max.get_text()))
                    func_range = (int(y_min.get_text()), int(y_max.get_text()))
                    last_domain = func_domain
                    last_range = func_range
                except ValueError:
                    func_domain = last_domain
                    func_range = last_range
                    x_min.value = str(last_domain[0])
                    x_max.value = str(last_domain[1])
                    y_min.value = str(last_range[0])
                    y_max.value = str(last_range[1])
            else:
                func_domain = last_domain
                func_range = last_range
            draw_graphing(230 if sidebar_state ==
                          EXTENDED else 0, calc_graph, rels, func_domain, func_range)
            buttons_pressed = pygame.mouse.get_pressed(num_buttons=3)
            clicked = calc_graph.handle_changes(buttons_pressed, clicked)

        # Draw the sidebar onto the screen
        if sidebar_state == EXTENDED:
            WIN.blit(sidebar[SIDEBAR_SURFACE], (0 - sidebar_anim_frames, 0))
            sidebar_anim_frames -= 25 if 0 < sidebar_anim_frames else 0
        else:
            WIN.blit(sidebar[SIDEBAR_SURFACE], (10, 10))

        pygame.display.update()


if __name__ == '__main__':
    main()

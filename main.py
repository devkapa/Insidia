import os
import sys

import pygame
import pickle
from random import choice
from pygame.locals import *

from commons import render_text, coloured_text, get_opus_path, get_current_path_main, TITLE, SUBHEADING, BACKGROUND_COLOUR
from calc.graphing import Graph
from calc.relations import Relation, RelationError

from widgets.textbox import Textbox
from widgets.button import Button
from tkinter import messagebox

# Versioning
version = "alpha-2.0"

# Enable double buffer for speed
flags = DOUBLEBUF

# Initialise pygame modules
pygame.font.init()
pygame.display.init()
pygame.mixer.init()

# RGB colour constants
WHITE = (255, 255, 255)
YELLOW = (253, 248, 140)
AQUA = (0, 255, 255)
TURQUOISE = (0, 206, 209)
PINK = (255, 225, 225)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (168, 168, 168)
BLACK = (0, 0, 0)
DEMO_PURPLE = (168, 113, 255)
SIDEBAR_COLOUR = (38, 39, 48)
SIDEBAR_HIGHLIGHT = (58, 59, 70)

# Size constants
WIDTH, HEIGHT = 1200, 800
SIDEBAR_WIDTH, SIDEBAR_HEIGHT = 250, HEIGHT
SIDEBAR_PADDING = 10

OPUS = pygame.USEREVENT + 5
EMPTY_EVENT = pygame.USEREVENT + 6
SNAPSHOT = pygame.USEREVENT + 7
SCROLL_UP = pygame.USEREVENT + 8
SCROLL_DOWN = pygame.USEREVENT + 9

CurrentPath = get_current_path_main()


# Loading screen messages
LOAD_MESSAGES = ["Compiling infinite digits of pi... this could take a while.",
                 "Conjuring up a mathematical genie to do the calculations for us... Sit tight!",
                 "Summoning the spirits of ancient mathematicians... hope they're in a good mood.",
                 "Preparing to launch the world's largest abacus... hold on tight!",
                 "Setting up a team of calculator-toting chimpanzees... standby for results.",
                 "Spinning up the quantum calculator... it may take some time to stabilize.",
                 "Assembling a team of mathemagicians to tackle your calculations... Abracadabra!",
                 "Initiating the mathematical singularity... brace for impact!"]

HOME_BODY_MESSAGES = [coloured_text(f"||col.{AQUA}||Math no longer has to be criminal.||col.{WHITE}|| Visualise stunning, interactive graphs, like the ||col.{DEMO_PURPLE}||demo||col.{WHITE}|| one here!", 17),
                      coloured_text(f"   (1) You're in ||col.{YELLOW}||PAN mode||col.{WHITE}||! ||col.{YELLOW}||Click and drag ||col.{WHITE}||on the graph to move around. Nice square wave, eh?", 17),
                      coloured_text(f"   (2) Alternatively, use the ||col.{YELLOW}||button||col.{WHITE}|| labelled ||col.{YELLOW}||POINT||col.{WHITE}||, which when hovering over the ", 17),
                      coloured_text("         graph will show you the points at which the line crosses. ", 17),
                      coloured_text(f"   (3) If you manage to get lost, the handy ||col.{YELLOW}||ORIGIN button||col.{WHITE}|| will set you back to the centre where you begun!", 17),
                      coloured_text(f"Discover more! Try your own equations. Head over to the ||col.{GREEN}||sidebar||col.{WHITE}|| to get started.", 17)
                      ]

# Frames per second constant
FPS = 120

# Enum values for code readability
HOME, GRAPHING, SAVE = 0, 1, 2
RETRACTED, EXTENDED = 0, 1
SIDEBAR_SURFACE, SIDEBAR_BUTTON, SIDEBAR_PAGES = 0, 1, 2


def square_wave(accuracy):
    """Create an equation for a square wave, given a certain accuracy."""
    i = 3
    eq = "y = (4/pi)*sin(pi*x)"
    while i <= accuracy:
        eq += f"+(4/pi)*(1/{i})*sin({i}*pi*x)"
        i += 2
    return eq


def get_sidebar(sidebar, status, saving_now):
    """
    Returns a tuple containing the sidebar information.
    If the sidebar is extended, it will return the sidebar surface and buttons.
    If it is closed, only the button to extend it will be returned.
    """
    if sidebar == EXTENDED:

        # Create the sidebar background
        sidebar_surface = pygame.Surface((SIDEBAR_WIDTH, SIDEBAR_HEIGHT))
        sidebar_surface.fill(SIDEBAR_COLOUR)

        # Draw a rect with an "X" close button on the sidebar top-right corner
        close_button = pygame.Rect(
            SIDEBAR_WIDTH - 30 - SIDEBAR_PADDING, SIDEBAR_PADDING, 30, 30)
        close_text = render_text("X", 35 if close_button.collidepoint(
            pygame.mouse.get_pos()) and not saving_now[0] else 30, font=TITLE)
        sidebar_surface.blit(close_text, (SIDEBAR_WIDTH -
                                          close_text.get_width() - SIDEBAR_PADDING, SIDEBAR_PADDING))

        # Draw each page as an interactive button on the sidebar
        pages = ["Home", "Graphing Calculator", "Opus"]
        pygame.display.set_caption(f"{pages[status]} • Insidia")
        for index, page in enumerate(pages):
            page_button = pygame.Surface(
                (SIDEBAR_WIDTH - (SIDEBAR_PADDING * 2), 30))
            page_rect = pygame.Rect(
                (SIDEBAR_PADDING, 100 + (index * 40)), (SIDEBAR_WIDTH - (SIDEBAR_PADDING * 2), 30))
            page_button.fill(SIDEBAR_HIGHLIGHT if status == index or (page_rect.collidepoint(
                pygame.mouse.get_pos()) and not saving_now[0]) else SIDEBAR_COLOUR)
            page_text = render_text(page, 20)
            page_button.blit(page_text, (SIDEBAR_PADDING, 5))
            sidebar_surface.blit(
                page_button, (SIDEBAR_PADDING, 100 + (index * 40)))
            pages[index] = page_rect

        return sidebar_surface, close_button, pages

    if sidebar == RETRACTED:
        # Return a rect with an arrow open button on the top-left corner of the screen
        open_button = pygame.Rect(SIDEBAR_PADDING, SIDEBAR_PADDING, 30, 30)
        open_text = render_text("»", 35 if open_button.collidepoint(
            pygame.mouse.get_pos()) and not saving_now[0] else 30, font=TITLE)
        return open_text, open_button


def draw_home(win, sidebar_offset, graph, home_rels):
    """Draw the home page of Insidia."""
    win.fill(BACKGROUND_COLOUR)
    title = render_text("Insidia: Your partner in math", 40, font=TITLE)
    win.blit(title, (sidebar_offset + 80, 80))

    # Create and draw the demo graph and its sliders relative to sidebar position
    win.blit(
        graph.create((-10, 10), (-2, 2), home_rels, (sidebar_offset + 80, 190), scale_x=graph.get_sliders()[0].value(),
                     scale_y=graph.get_sliders()[1].value()),
        (sidebar_offset + 80, 155))
    graph.set_pos((sidebar_offset + 80, 155))
    y_accumulated = 0
    for slider in graph.get_sliders():
        surface = slider.create()
        win.blit(surface, (sidebar_offset + 700, 155 + y_accumulated))
        slider.set_pos((sidebar_offset + 700, 155 + y_accumulated))
        y_accumulated += surface.get_height() + 20
    x_accumulated = 0
    for button in graph.get_buttons():
        button.create(win, graph.get_mode(), sidebar_offset + 710 +
                      x_accumulated, 155 + y_accumulated)
        x_accumulated += button.size[0] + 15
    y_accumulated = 0
    for message in HOME_BODY_MESSAGES:
        win.blit(message, (sidebar_offset + 80, 490 + y_accumulated))
        y_accumulated += message.get_height() + 25


def draw_graphing(win, sidebar_offset, graph, rels, func_domain, func_range):
    """Draw the graphing calculator page of Insidia."""
    win.fill(BACKGROUND_COLOUR)

    # Create and draw the main graph and its sliders, equation inputs and buttons relative to the sidebar position
    graph.set_pos((sidebar_offset + 70, 50))
    y_accumulated = 0
    for slider in graph.get_sliders():
        surface = slider.create()
        win.blit(surface, (sidebar_offset +
                           graph.size[0] + 90, 50 + y_accumulated))
        slider.set_pos(
            (sidebar_offset + graph.size[0] + 90, 50 + y_accumulated))
        y_accumulated += surface.get_height() + 20
    x_accumulated = 0
    for i, button in enumerate(graph.get_buttons()):
        if i != 3:
            button.create(win, graph.get_mode(), sidebar_offset + graph.size[0] + 100 +
                          x_accumulated, 50 + y_accumulated)
            if i < 2:
                x_accumulated += button.size[0] + 15
            continue
        button.create(win, graph.get_mode(), sidebar_offset + graph.size[0] + 100 +
                      x_accumulated + 5, 50 + y_accumulated + 80)
    y_accumulated += 70
    x_accumulated = 0
    for i, textbox in enumerate(graph.get_d_r_boxes()):
        textbox.create(win, sidebar_offset +
                       graph.size[0] + 100 + x_accumulated, 50 + y_accumulated)
        if i == 1:
            y_accumulated += 60
            x_accumulated -= textbox.size[0] + 15
            continue
        x_accumulated += textbox.size[0] + 15
    y_accumulated += 70
    for textbox in graph.get_textboxes():
        textbox.create(win, sidebar_offset +
                       graph.size[0] + 100, 50 + y_accumulated)
        y_accumulated += textbox.size[1] + 40
    win.blit(graph.create(func_domain, func_range, list(rels.values()), (sidebar_offset + 70, 50),
                          scale_x=graph.get_sliders()[0].value(), scale_y=graph.get_sliders()[1].value()),
             (sidebar_offset + 70, 50))


def draw_save(win, sidebar_offset, save_button, save_textbox, opus_saves, opus_removal_buttons, opus_load_buttons, saving_now, snapshot_button, scroll_list_offset, scroll_down, scroll_up):
    """Draw the Opus page of Insidia."""
    win.fill(BACKGROUND_COLOUR)
    title = render_text("Insidia: Opus", 40, font=TITLE)
    win.blit(title, (sidebar_offset + 80, 80))
    subtitle = render_text("Export your graphs with Insidia Opus. Save a graph (.opus) to use in Insidia or take a snapshot (.png).", 18, font=SUBHEADING)
    win.blit(subtitle, (sidebar_offset + 80, 80 + title.get_height() + 20))
    save_button.create(win, 0, sidebar_offset + 80, 80 + title.get_height() + 40 + subtitle.get_height())
    snapshot_button.create(win, 0, sidebar_offset + 100 + save_button.size[0], 80 + title.get_height() + 40 + subtitle.get_height())

    # If the save menu is currently open, render accordingly
    if saving_now[0]:
        # Draw a window in the centre of the screen with a textbox where the user can input the file name
        rect = pygame.Rect(WIDTH/2 - 400/2, HEIGHT/2 - 150/2, 400, 150)
        pygame.draw.rect(win, GRAY, rect)
        save_title = render_text("Export current graph", 20, font=SUBHEADING)
        save_title_shadow = render_text("Export current graph", 20, font=SUBHEADING, color=GREEN)
        cancel_text_shadow = render_text("Or, press Escape to cancel.", 16, color=WHITE)
        cancel_text = render_text("Or, press Escape to cancel.", 16, color=RED)
        win.blit(save_title_shadow, (WIDTH/2 - 400/2 + 10 + 1, HEIGHT/2 - 170/2 + 20 + 1))
        win.blit(save_title, (WIDTH/2 - 400/2 + 10, HEIGHT/2 - 170/2 + 20))
        save_textbox.create(win, WIDTH/2 - 400/2 + 20, HEIGHT/2 - 170/2 + 40 + save_title.get_height())
        win.blit(cancel_text, (WIDTH/2 - 400/2 + 10 + 1, HEIGHT/2 - 170/2 + 80 + save_title.get_height() + save_textbox.size[1] + 1))
        win.blit(cancel_text_shadow, (WIDTH/2 - 400/2 + 10, HEIGHT/2 - 170/2 + 80 + save_title.get_height() + save_textbox.size[1]))
        save_textbox.set_active(True)
    else:
        # Otherwise, watch for button events and monitor changes in opus saves.
        save_button.on_hover()
        snapshot_button.on_hover()
        saved_graphs_title = render_text("Saved Opus Graphs", 18, font=SUBHEADING)
        win.blit(saved_graphs_title, (sidebar_offset + 80, 80 + title.get_height() + 40 + subtitle.get_height() + save_button.size[1] + 30))
        scroll_list = pygame.Surface((600, 550))
        scroll_list.fill(BACKGROUND_COLOUR)
        y_accumulated = 0
        for save in opus_saves:
            text = render_text(opus_saves[save].name, 24)
            text_shadow = render_text(opus_saves[save].name, 24, color=TURQUOISE)
            coords = (0, y_accumulated)
            save_rect = pygame.Rect(coords[0], coords[1] - scroll_list_offset, 600, text.get_height() + 30)
            pygame.draw.rect(scroll_list, SIDEBAR_COLOUR, save_rect, border_radius=10)
            if opus_removal_buttons[opus_saves[save]].last_surface is not None:
                opus_removal_buttons[opus_saves[save]].on_hover()
            opus_removal_buttons[opus_saves[save]].create(scroll_list, 0, coords[0] + 600 - 50, coords[1] + ((text.get_height() + 30)/2) - 20 - scroll_list_offset)
            opus_removal_buttons[opus_saves[save]].pos = (coords[0] + 600 - 50 + sidebar_offset + 80, 80 + title.get_height() + 40 + subtitle.get_height() + saved_graphs_title.get_height() + save_button.size[1] + 50 + coords[1] + ((text.get_height() + 30)/2) - 20 - scroll_list_offset)
            if opus_load_buttons[opus_saves[save]].last_surface is not None:
                opus_load_buttons[opus_saves[save]].on_hover()
            opus_load_buttons[opus_saves[save]].create(scroll_list, 0, coords[0] + 600 - 100, coords[1] + ((text.get_height() + 30)/2) - 20 - scroll_list_offset)
            opus_load_buttons[opus_saves[save]].pos = (coords[0] + 600 - 100 + sidebar_offset + 80, coords[1] + ((text.get_height() + 30)/2) - 20 - scroll_list_offset + 80 + title.get_height() + 40 + subtitle.get_height() + saved_graphs_title.get_height() + save_button.size[1] + 50)
            scroll_list.blit(text_shadow, (coords[0] + 10 + 1, 1 + coords[1] + ((text.get_height() + 30)/2) - (text.get_height()/2) - scroll_list_offset))
            scroll_list.blit(text, (coords[0] + 10, coords[1] + ((text.get_height() + 30)/2) - (text.get_height()/2) - scroll_list_offset))
            y_accumulated += text.get_height() + 50
        win.blit(scroll_list, (sidebar_offset + 80, 80 + title.get_height() + 40 + subtitle.get_height() + saved_graphs_title.get_height() + save_button.size[1] + 50))
        if scroll_up.last_surface is not None:
            scroll_up.on_hover()
        if scroll_down.last_surface is not None:
            scroll_down.on_hover()
        scroll_up.create(win, 0, sidebar_offset + 100 + scroll_list.get_width(), 80 + title.get_height() + 40 + subtitle.get_height() + save_button.size[1] + 30)
        scroll_down.create(win, 0, sidebar_offset + 100 + scroll_list.get_width(), 80 + title.get_height() + 40 + subtitle.get_height() + save_button.size[1] + 50 + scroll_down.size[1])


def main():
    # Create an opaque window surface with defined width and height, and set a title
    win = pygame.display.set_mode((WIDTH, HEIGHT), flags, 8)
    win.set_alpha(None)
    pygame.display.set_caption("Insidia")

    # Set the icon of the window
    icon = pygame.image.load(os.path.join(
        CurrentPath, 'assets', 'textures', 'logo.png'))
    pygame.display.set_icon(icon)

    icon_splash = pygame.transform.scale(icon, (400, 400))

    # Display a random loading message whilst pygame initialises
    init_text = render_text(choice(LOAD_MESSAGES), 30, font=TITLE)
    win.blit(icon_splash, (WIDTH / 2 - icon_splash.get_width() /
                           2, HEIGHT / 2 - icon_splash.get_height() / 2 - init_text.get_height()))
    win.blit(init_text, (WIDTH / 2 - init_text.get_width() /
                         2, HEIGHT / 2 + icon_splash.get_height() / 2 + 10))
    pygame.display.update()

    # Convert the demo square wave to a Relation object that can be passed to the graph
    home_rels = [Relation(square_wave(31), DEMO_PURPLE)]

    # Initialise pygame's clock and start the game loop
    clock = pygame.time.Clock()
    running = True

    # Set the initial state to the title screen
    current_state = HOME
    # update_message = ""

    # Set the sidebar to default open
    sidebar_state = EXTENDED
    sidebar_anim_frames = 0

    # A variable to store which Surface is currently clicked, if any
    clicked = None

    # Initialise both the demo and main graphs, with the main graph including equation inputs and a clear button
    demo_graph = Graph((600, 300))
    calc_graph = Graph((650, 700), equations=5, clear=True)

    # Cache the last known Relations and set domain/range on the main graph
    rels = {}
    last_domain = (-10, 10)
    last_range = (-5, 5)

    # Cache to hold Insidia: Opus data
    save_button = Button(os.path.join(CurrentPath, 'assets', 'textures', 'add.png'), (150, 60), OPUS, 0, "Add Opus Plot")
    snapshot_button = Button(os.path.join(CurrentPath, 'assets', 'textures', 'snapshot.png'), (150, 60), SNAPSHOT, 0, "Snapshot")
    save_textbox = Textbox((350, 30), 18, "Name your graph", BLACK, placeholder="Type a graph name...", background_colour=GRAY)
    opus_saves = {}
    opus_removal_buttons = {}
    opus_load_buttons = {}
    saving_now = (False, None)
    scroll_list_offset = 0
    scroll_down = Button(os.path.join(CurrentPath, 'assets', 'textures', 'down.png'), (60, 60), SCROLL_DOWN, 0, "Down")
    scroll_up = Button(os.path.join(CurrentPath, 'assets', 'textures', 'up.png'), (60, 60), SCROLL_UP, 0, "Up")

    # Create Opus directory if it does not exist
    if not os.path.isdir(os.path.join(get_opus_path(), 'opus')):
        os.mkdir(os.path.join(get_opus_path(), 'opus'))

    while running:

        # Limit the loop to run only 60 times per second
        clock.tick(FPS)

        # Get sidebar surface and button rects
        sidebar = get_sidebar(sidebar_state, current_state, saving_now)

        # Iterate through pygame events
        for event in pygame.event.get():

            # Exit the program if the user quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Change the mode of the graph appropriate to which event occurred
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
                    textbox.set_validity(True)
                for textbox in calc_graph.get_d_r_boxes():
                    textbox.value = textbox.default
                calc_graph.reset()

            # Handle all custom Opus events
            if event.type == OPUS:
                if len(calc_graph.lines) > 0:
                    saving_now = (True, OPUS)
                else:
                    messagebox.showerror("Error", "The current graph is empty. Go add some equations in the Graphing Calculator, then try again.")

            if event.type == SNAPSHOT:
                if len(calc_graph.lines) > 0:
                    saving_now = (True, SNAPSHOT)
                else:
                    messagebox.showerror("Error", "The current graph is empty. Go add some equations in the Graphing Calculator, then try again.")

            if event.type == SCROLL_UP:
                scroll_list_offset -= 30
                if scroll_list_offset < 0:
                    scroll_list_offset = 0

            if event.type == SCROLL_DOWN:
                scroll_list_offset += 30
                px = (len(opus_removal_buttons)*100) - 550
                if scroll_list_offset > px:
                    scroll_list_offset = px

            # Check if a key was pressed whilst a textbox was selected
            if event.type == pygame.KEYDOWN:
                for textbox in calc_graph.get_textboxes() + calc_graph.get_d_r_boxes():
                    if textbox.active:
                        if event.key == pygame.K_RETURN:
                            textbox.set_active(False)
                        elif event.key == pygame.K_BACKSPACE:
                            textbox.backspace()
                        elif event.key in Textbox.ARROWS:
                            textbox.move_cursor(event.key)
                        elif event.key in Textbox.WHITELIST:
                            textbox.add_text(event.unicode)

                # Handle Opus file saving
                if saving_now[0]:
                    save_textbox.set_active(True)
                    if event.key == pygame.K_RETURN:
                        real_value = "".join(x for x in save_textbox.value if x.isalnum())
                        if save_textbox.value != "" and real_value != "":
                            save_textbox.set_active(False)
                            save_textbox.set_validity(True)

                            # If an Opus save was to be created, do as such
                            if saving_now[1] == OPUS:
                                fake_graph = calc_graph.save(save_textbox.value)
                                with open(os.path.join(get_opus_path(), 'opus', f'{real_value.lower()}.opus'), 'wb') as f:
                                    pickle.dump(fake_graph, f)
                                    opus_saves[f] = fake_graph
                                    removal_button = Button(os.path.join(CurrentPath, 'assets', 'textures', 'remove.png'), (40, 40), EMPTY_EVENT, 0, "Del", background_colour=SIDEBAR_COLOUR)
                                    opus_removal_buttons[fake_graph] = removal_button
                                    load_button = Button(os.path.join(CurrentPath, 'assets', 'textures', 'load.png'), (40, 40), EMPTY_EVENT, 0, "Load", background_colour=SIDEBAR_COLOUR)
                                    opus_load_buttons[fake_graph] = load_button
                                scroll_list_offset = 0
                                messagebox.showinfo("Save Opus Graph", f"Successfully saved opus graph to \"{str(os.path.join(get_opus_path(), 'opus', f'{real_value.lower()}.opus'))}\".")

                            # If an image snapshot was to be created, do as such
                            if saving_now[1] == SNAPSHOT:
                                pygame.image.save(calc_graph.last_surface, os.path.join(get_opus_path(), 'opus', f'{real_value.lower()}.png'))
                                messagebox.showinfo("Snapshot Opus Graph", f"Successfully saved snapshot to \"{str(os.path.join(get_opus_path(), 'opus', f'{real_value.lower()}.png'))}\".")

                            saving_now = (False, None)
                            save_textbox.value = ""
                        else:
                            save_textbox.set_validity(False)
                    elif event.key == pygame.K_ESCAPE:
                        saving_now = (False, None)
                    elif event.key == pygame.K_BACKSPACE:
                        save_textbox.backspace()
                    elif event.key in Textbox.WHITELIST:
                        save_textbox.add_text(event.unicode)

            # Check if the user clicked the mouse
            if event.type == pygame.MOUSEBUTTONDOWN and not saving_now[0]:

                # Change sidebar state if button is pressed
                if sidebar[SIDEBAR_BUTTON].collidepoint(event.pos):
                    if sidebar_state == EXTENDED:
                        sidebar_state = RETRACTED
                        calc_graph.extend(850)
                    else:
                        sidebar_state = EXTENDED
                        calc_graph.extend(650)
                        sidebar_anim_frames = SIDEBAR_WIDTH

                if current_state == SAVE:
                    # Post save or snapshot events if buttons are clicked
                    if save_button.last_surface is not None:
                        save_button.on_click()

                    if snapshot_button.last_surface is not None:
                        snapshot_button.on_click()

                    # Post scroll events if buttons are clicked
                    if scroll_up.last_surface is not None:
                        scroll_up.on_click()

                    if scroll_down.last_surface is not None:
                        scroll_down.on_click()

                    # Handle correct removals of Opus saves and loads
                    removal = False
                    for save in opus_saves:
                        if opus_removal_buttons[opus_saves[save]].on_click():
                            delete = messagebox.askquestion('Delete Opus Graph', f'Are you sure you want to delete \"{opus_saves[save].name}\"?',
                                                            icon='warning')
                            if delete == 'yes':
                                os.remove(save.name)
                                removal = True
                        if opus_load_buttons[opus_saves[save]].on_click():
                            load = messagebox.askquestion('Load Opus Graph', f'Are you sure you want to load \"{opus_saves[save].name}\"?',
                                                          icon='warning')
                            if load == 'yes':

                                for textbox in calc_graph.get_textboxes():
                                    textbox.reset()
                                    textbox.set_validity(True)
                                for textbox in calc_graph.get_d_r_boxes():
                                    textbox.value = textbox.default
                                calc_graph.reset()

                                for line in opus_saves[save].lines:
                                    for textbox in calc_graph.get_textboxes():
                                        if textbox.value != "":
                                            continue
                                        textbox.value = line
                                        break

                                current_state = GRAPHING
                                messagebox.showinfo("Load Opus Graph", f"Successfully loaded \"{opus_saves[save].name}\".")

                    if removal:
                        opus_saves = {}
                        opus_load_buttons = {}
                        opus_removal_buttons = {}
                        for file in os.listdir(os.path.join(get_opus_path(), 'opus')):
                            if file.lower().endswith(".opus"):
                                with open(os.path.join(get_opus_path(), 'opus', file), "rb") as input_file:
                                    loaded = pickle.load(input_file)
                                    opus_saves[input_file] = loaded
                                    removal_button = Button(os.path.join(CurrentPath, 'assets', 'textures', 'remove.png'), (40, 40), EMPTY_EVENT, 0, "Del", background_colour=SIDEBAR_COLOUR)
                                    opus_removal_buttons[loaded] = removal_button
                                    load_button = Button(os.path.join(CurrentPath, 'assets', 'textures', 'load.png'), (40, 40), EMPTY_EVENT, 0, "Load", background_colour=SIDEBAR_COLOUR)
                                    opus_load_buttons[loaded] = load_button
                                scroll_list_offset = 0

                # Reload sidebar after state change
                sidebar = get_sidebar(sidebar_state, current_state, saving_now)

                # Change program state if sidebar page button is pressed
                if len(sidebar) > SIDEBAR_PAGES:
                    for state in [HOME, GRAPHING, SAVE]:
                        if sidebar[SIDEBAR_PAGES][state].collidepoint(event.pos):
                            if state == SAVE:
                                if os.path.isdir(os.path.join(get_opus_path(), 'opus')):
                                    opus_saves = {}
                                    opus_load_buttons = {}
                                    opus_removal_buttons = {}
                                    for file in os.listdir(os.path.join(get_opus_path(), 'opus')):
                                        if file.lower().endswith(".opus"):
                                            with open(os.path.join(get_opus_path(), 'opus', file), "rb") as input_file:
                                                loaded = pickle.load(input_file)
                                                opus_saves[input_file] = loaded
                                                removal_button = Button(os.path.join(CurrentPath, 'assets', 'textures', 'remove.png'), (40, 40), EMPTY_EVENT, 0, "Del", background_colour=SIDEBAR_COLOUR)
                                                opus_removal_buttons[loaded] = removal_button
                                                load_button = Button(os.path.join(CurrentPath, 'assets', 'textures', 'load.png'), (40, 40), EMPTY_EVENT, 0, "Load", background_colour=SIDEBAR_COLOUR)
                                                opus_load_buttons[loaded] = load_button
                                            scroll_list_offset = 0
                            if not Button.CLICK_CHANNEL.get_busy():
                                Button.CLICK_CHANNEL.play(Button.CLICK_SOUND)
                            current_state = state

        # Display the homepage if the program state is HOME.
        if current_state == HOME:
            draw_home(win, 230 if sidebar_state == EXTENDED else 0, demo_graph, home_rels)
            buttons_pressed = pygame.mouse.get_pressed(num_buttons=3)
            clicked = demo_graph.handle_changes(buttons_pressed, clicked)

        # Display the Insidia: Opus page if the program state is SAVE
        if current_state == SAVE:
            draw_save(win, 230 if sidebar_state == EXTENDED else 0, save_button, save_textbox, opus_saves, opus_removal_buttons, opus_load_buttons, saving_now, snapshot_button, scroll_list_offset, scroll_down, scroll_up)

        # Display the graphing calculator if the program state is HOME.
        if current_state == GRAPHING:
            # If an equation input is no longer active, convert and queue it to be graphed
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
                            textbox.message_shown = False
                        else:
                            if textbox in rels:
                                rels.pop(textbox)
                            textbox.set_validity(True)
                            textbox.message_shown = False
                    except RelationError:
                        if not textbox.message_shown:
                            messagebox.showerror("Error", f"{textbox.title} has an invalid expression." +
                                                 "\nIf multiplying two terms, e.g. 2sin(x), " +
                                                          "try adding a *, e.g. 2*sin(x)")
                            textbox.message_shown = True
                        textbox.set_validity(False)
                        if textbox in rels:
                            rels.pop(textbox)
            active = False

            # If a domain or range input is no longer active, queue it to be graphed
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

            # Draw the window
            draw_graphing(win, 230 if sidebar_state == EXTENDED else
                          0, calc_graph, rels, func_domain, func_range)
            buttons_pressed = pygame.mouse.get_pressed(num_buttons=3)
            clicked = calc_graph.handle_changes(buttons_pressed, clicked)

        # Draw the sidebar onto the screen
        if sidebar_state == EXTENDED:
            win.blit(sidebar[SIDEBAR_SURFACE], (0 - sidebar_anim_frames, 0))
            sidebar_anim_frames -= 25 if 0 < sidebar_anim_frames else 0
        else:
            win.blit(sidebar[SIDEBAR_SURFACE], (10, 10))

        pygame.display.update()


if __name__ == '__main__':
    main()

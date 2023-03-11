import os
import sys
import pygame
import symengine
import sympy
from multiprocessing.pool import ThreadPool
from symengine import Symbol, sympify
from widgets.slider import Slider
from widgets.button import Button
from widgets.textbox import Textbox
from tkinter import messagebox
from random import choice

# RGB colour constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (100, 100, 100)
BACKGROUND_GREY = (239, 239, 239)

# Graph curve colours
RED = (139, 0, 0)
ORANGE = (255, 140, 0)
YELLOW = (184, 134, 11)
GREEN = (0, 100, 0)
BLUE = (0, 0, 139)
PURPLE = (148, 0, 211)
CYAN = (0, 139, 139)
MAGENTA = (139, 0, 139)
GRAY = (169, 169, 169)
BROWN = (101, 67, 33)
TURQUOISE = (0, 206, 209)
GOLD = (218, 165, 32)
INDIGO = (75, 0, 130)
SALMON = (233, 150, 122)
SEA_GREEN = (143, 188, 143)
SLATE_BLUE = (72, 61, 139)
OLIVE_GREEN = (85, 107, 47)
LIME_GREEN = (50, 205, 50)
SKY_BLUE = (135, 206, 235)
PINK = (255, 20, 147)
BEIGE = (205, 183, 158)
TAN = (138, 90, 34)
CORAL = (205, 91, 69)
LAVENDER = (150, 123, 182)

COLOURS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, CYAN, MAGENTA, GRAY, BROWN, TURQUOISE, GOLD, INDIGO,
           SALMON, SEA_GREEN, SLATE_BLUE, OLIVE_GREEN, LIME_GREEN, SKY_BLUE, PINK, BEIGE, TAN, CORAL, LAVENDER]

# Font file names
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
    'Oxanium-Regular.ttf', 'press-start.ttf'

# Predefined factorial object for error checking
FACTORIAL = sympify(sympy.sympify("factorial(x)"))

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


def in_viewport(coordinate, viewport, viewport_max):
    """Returns whether the given coordinate is within the range of the viewport"""
    return viewport[0] <= coordinate[0] <= viewport_max[0] and viewport[1] <= coordinate[1] <= viewport_max[1]


def low_res_warning(x):
    """Warn the user that a graph cannot be fully evaluated with a tkinter messagebox"""
    all_graphs = "\n   • ".join(x)
    warning = f"""The following graph(s) cannot be fully evaluated:\n   • {all_graphs}\nEvaluating at low resolution"""
    messagebox.showwarning("Warning", warning)


def multisolver(expression):
    """
    Recursively resolve an expression and replace all fractions with Rational objects.
    This ensures any curve with an odd power renders correctly.
    """
    for index, sub_expr in enumerate(expression.args):
        if type(sub_expr) == symengine.Pow:
            if type(sub_expr.args[1]) == symengine.Rational:
                num, den = sub_expr.args[1].get_num_den()
                real_root = sympify(sympy.real_root(
                    sympy.Pow(sub_expr.args[0], num), den))
                expression = expression.replace(
                    expression.args[index], real_root)
        else:
            expression = expression.replace(
                sub_expr, multisolver(sub_expr))
    return expression


def factorial_checker(expression):
    """
    Recursively observe an expression to check for a factorial calculation.
    """
    if expression == FACTORIAL:
        return True
    elif type(expression) != tuple:
        found = False
        for i in expression.args:
            found = factorial_checker(i) if not found else True
        return found
    elif FACTORIAL in expression.args:
        return True
    else:
        try:
            return factorial_checker(expression.args)
        except AttributeError:
            return False


def calculate_x_y(relation, all_x, all_y):
    """
    Create lists of all points to be drawn on a graph. If the graph cannot be solved by symengine's algorithms,
    or if the solution requires complex numbers, then use an alternate solving method which is less accurate
    and must render at a lower resolution (every 0.1 x instead of 0.01 x).
    """
    x_exprs, y_exprs = relation.f()

    symbol_x = Symbol('x')
    symbol_y = Symbol('y')

    lines_to_draw = []

    # Iterate through all the functions for Y.
    for expr in y_exprs.args:

        # Recursively resolve if necessary
        if type(expr) == symengine.Pow:
            if type(expr.args[1]) == symengine.Rational:
                num, den = expr.args[1].get_num_den()
                real_root = sympify(
                    sympy.real_root(sympy.Pow(expr.args[0], num), den))
                expr = real_root
            else:
                expr = multisolver(expr)

        points = []

        # Iterate through X values
        for x_val in all_x:

            # Disallow factorial of negative integers from being calculated (prevent pygame segmentation fault)
            if factorial_checker(expr):
                if x_val < 0 and x_val % 1 == 0:
                    if len(points) > 1:
                        lines_to_draw.append(points)
                    points = []
                    continue

            # Substitute current X into current function of Y
            y_val = expr.xreplace({symbol_x: x_val})

            # Attempt to numerically evaluate Y
            try:
                y_val = symengine.Float(y_val)
            except RuntimeError:
                pass

            # Discard Y if it is complex
            if not y_val.is_real:
                if len(points) > 1:
                    lines_to_draw.append(points)
                points = []
                continue

            # Discard Y if it is not in the graph's range
            if y_val < all_y[0] or y_val > all_y[-1]:
                if len(points) > 1:
                    lines_to_draw.append(points)
                points = []
                continue

            # Add Y to the current line
            points.append((x_val, y_val))

        # Add leftover lines
        if len(points) > 1:
            lines_to_draw.append(points)

    # Get lines for when there are no solutions for Y (e.g. x=5)
    if len(y_exprs.args) == 0:

        # Iterate through all the functions for X.
        for expr in x_exprs.args:

            # Recursively resolve if necessary
            if type(expr) == symengine.Pow:
                if type(expr.args[1]) == symengine.Rational:
                    num, den = expr.args[1].get_num_den()
                    real_root = sympify(
                        sympy.real_root(sympy.Pow(expr.args[0], num), den))
                    expr = real_root
                else:
                    expr = multisolver(expr)

            points = []

            for y_val in all_y:

                # Disallow factorial of negative integers from being calculated (prevent pygame segmentation fault)
                if factorial_checker(expr):
                    if y_val < 0 and x_val % 1 == 0:
                        if len(points) > 1:
                            lines_to_draw.append(points)
                        points = []
                        continue

                # Substitute current Y into current function of X
                x_val = expr.xreplace({symbol_y: y_val})

                # Attempt to numerically evaluate Y
                try:
                    x_val = symengine.Float(x_val)
                except RuntimeError:
                    pass

                # Discard X if it is complex
                if not x_val.is_real:
                    if len(points) > 1:
                        lines_to_draw.append(points)
                    points = []
                    continue

                # Discard X if it is not in the graph's domain
                if x_val < all_x[0] or x_val > all_x[-1]:
                    if len(points) > 1:
                        lines_to_draw.append(points)
                    points = []
                    continue

                # Add X to the current line
                points.append((x_val, y_val))

            # Add leftover lines
            if len(points) > 1:
                lines_to_draw.append(points)

    alternate_renders = []

    # Iterately solve for g(x) = 0 if no solutions were possible through real function notation
    if len(lines_to_draw) == 0:

        # Only calculate if left-hand-side is different (has a relation) to right side
        if relation.lhs != relation.rhs:
            try:

                # Rearrange for 0
                ex = sympify(relation.lhs + " - " + relation.rhs)

                # Add point if g(x) is close to zero
                for x_val in all_x:
                    if not (x_val * 10).is_integer():
                        continue
                    for y_val in all_y:
                        if not (y_val * 10).is_integer():
                            continue
                        ans = ex.xreplace(
                            {symbol_x: x_val, symbol_y: y_val})
                        if ans.is_real and -0.1 <= ans <= 0.1:
                            alternate_renders.append((x_val, y_val))
            except:
                pass

    return lines_to_draw, alternate_renders


class Graph:
    """
    The graph structure allows for the drawing of a cartesian plane, given a domain and range.
    Once passed a Relation, it can calculate and render dynamically onto the graph.
    It also contains all necessary methods so that the graph can be controlled by user input.
    """

    # Enum values to handle built-in buttons
    PAN, TOOLTIP = 0, 1
    PAN_EVENT, TOOLTIP_EVENT, RESET_EVENT, CLEAR_EVENT = pygame.USEREVENT + \
                                                         1, pygame.USEREVENT + 2, pygame.USEREVENT + 3, pygame.USEREVENT + 4

    mode: int
    size: tuple
    offset_x: int
    offset_y: int
    cache: dict
    last_surface: pygame.Surface | None
    viewing_surface: pygame.Surface
    pos: tuple | None
    mouse_pos: tuple | None
    clicked: bool
    sliders: list
    buttons: list
    textboxes: list
    d_r_boxes: list
    lines: dict
    alternate: dict
    used_colours: list
    pool: ThreadPool

    # Initialise generic empty graph with default values
    def __init__(self, size, equations=0, clear=False) -> None:
        self.mode = self.PAN
        self.size = size
        self.offset_x, self.offset_y = 0, 0
        self.func_domain, self.func_range = 0, 0
        self.scale_x, self.scale_y = 0, 0
        self.plotting_size_x, self.plotting_size_y = 0, 0
        self.cache = {'func_domain': None, 'func_range': None,
                      'scale_x': None, 'scale_y': None}
        self.last_surface = None
        self.pos = None
        self.mouse_pos = None
        self.clicked = False
        self.sliders = [Slider(1, 200, 200, 10, 10, default=40, name="X Axis Scale"),
                        Slider(1, 200, 200, 10, 10, default=40, name="Y Axis Scale")]
        self.buttons = [
            Button(os.path.join(CurrentPath, 'assets', 'textures', 'pan_cursor.png'), (55, 50), self.PAN_EVENT, 0,
                   "Pan"),
            Button(os.path.join(
                CurrentPath, 'assets', 'textures', 'tooltip_cursor.png'), (55, 50), self.TOOLTIP_EVENT, 1, "Point"),
            Button(os.path.join(CurrentPath, 'assets', 'textures', 'reset.png'),
                   (55, 50), self.RESET_EVENT, -1, "Origin")]
        self.textboxes = []
        self.d_r_boxes = [Textbox((60, 30), 18, "X-Min", WHITE, default="-10"),
                          Textbox((60, 30), 18, "X-Max", WHITE, default="10"),
                          Textbox((60, 30), 18, "Y-Min", WHITE, default="-10"),
                          Textbox((60, 30), 18, "Y-Max", WHITE, default="10")]
        self.lines = {}
        self.alternate = {}
        self.used_colours = []
        if equations != 0:
            i = 0
            while i < equations:
                self.add_textbox()
                i += 1
        if clear:
            self.add_clear_button()
        self.pool = ThreadPool(processes=1)

    # Extend the size of the graph to the size of the window, if needed.
    def extend(self, size_x) -> None:
        self.size = (size_x, self.size[1])

    # Getter for domain and range textbox objects
    def get_d_r_boxes(self) -> list:
        return self.d_r_boxes

    # Generate a textbox with a random colour that hasn't been used before
    def add_textbox(self) -> None:
        random_colour = choice(
            [i for i in COLOURS if i not in self.used_colours])
        self.used_colours.append(random_colour)
        self.textboxes.append(
            Textbox((200, 30), 18, "Equation " + str(len(self.textboxes) + 1), random_colour))

    # Return equation input textboxes
    def get_textboxes(self) -> list:
        return self.textboxes

    # Return if the graph surface has been clicked
    def get_clicked(self) -> bool:
        return self.clicked

    # Set the clicked state of the button and the mouse position if provided.
    def set_clicked(self, bool, mouse_pos=None) -> None:
        self.clicked = bool
        self.mouse_pos = mouse_pos

    # Cache graph's current position when it is plotted 
    def set_pos(self, pos) -> None:
        self.pos = pos

    # Get the graph's last known position 
    def get_pos(self) -> tuple:
        return self.pos

    # Change the graph mode between PAN or POINT
    def set_mode(self, mode) -> None:
        self.mode = mode

    # Get the current graph mode
    def get_mode(self) -> int:
        return self.mode

    # If the graph has been clicked, get it's last known position
    def get_mouse_pos(self) -> tuple:
        return self.mouse_pos

    # Return scale sliders
    def get_sliders(self) -> list:
        return self.sliders

    # Return utility buttons
    def get_buttons(self) -> list:
        return self.buttons

    # Render an extra button to clear equation inputs if the graph has any
    def add_clear_button(self) -> None:
        clear_btn = Button(os.path.join(
            CurrentPath, 'assets', 'textures', 'broom.png'), (50, 110), self.CLEAR_EVENT, -1, "Clear")
        self.buttons.append(clear_btn)

    # Offset the graph horizontally. If it exceeds the plotting area, reposition.
    def shift_x(self, val) -> None:
        if self.offset_x + val > self.plotting_size_x / 2 - self.size[0] / 2:
            self.offset_x = self.plotting_size_x / 2 - self.size[0] / 2
            return
        if self.offset_x + val < -(self.plotting_size_x / 2 - self.size[0] / 2):
            self.offset_x = int(-(self.plotting_size_x / 2 - self.size[0] / 2))
            return
        self.offset_x += val

    # Offset the graph vertically. If it exceeds the plotting area, reposition.
    def shift_y(self, val) -> None:
        if self.offset_y + val > self.plotting_size_y / 2 - self.size[1] / 2:
            self.offset_y = self.plotting_size_y / 2 - self.size[1] / 2
            return
        if self.offset_y + val < -(self.plotting_size_y / 2 - self.size[1] / 2):
            self.offset_y = int(-(self.plotting_size_y / 2 - self.size[1] / 2))
            return
        self.offset_y += val

    # Reset the slider values to defaults, and return the offset to the origin position
    def reset(self) -> None:
        self.offset_x, self.offset_y = 0, 0
        for slider in self.sliders:
            slider.reset()

    # Given a Relation and the scope of the graph, sketch the lines (if function-like), otherwise draw points
    def sketch(self, all_x, all_y, relation, scale_x, scale_y, graph_surface, change) -> str | None:
        
        # Get the centre of the graph
        origin = (self.plotting_size_x / 2, self.plotting_size_y / 2)

        # If the relation has already been calculated, don't waste resources recalculating it
        if (relation not in self.lines and relation not in self.alternate) or change:

            # Asynchronously calculate X and Y values to prevent pygame freezing
            async_result = self.pool.apply_async(calculate_x_y, (relation, all_x, all_y,))

            lines_to_draw, alternate_renders = async_result.get()

            self.lines[relation] = lines_to_draw
            self.alternate[relation] = alternate_renders

            # Given the Relation being drawn is new, return a string to send a warning message
            if len(alternate_renders) > 0:
                if len(self.lines[relation]) == 0 and relation in self.alternate:
                    for point in self.alternate[relation]:
                        pygame.draw.circle(
                            graph_surface, relation.get_colour(),
                            (origin[0] + (point[0] * scale_x), origin[1] - (point[1] * scale_y)), 1)
                return str(relation.get_expression())

        # Draw the cached values
        if len(self.lines[relation]) == 0 and relation in self.alternate:
            for point in self.alternate[relation]:
                pygame.draw.circle(
                    graph_surface, relation.get_colour(),
                    (origin[0] + (point[0] * scale_x), origin[1] - (point[1] * scale_y)), 1)

        for line in self.lines[relation]:
            pygame.draw.aalines(graph_surface, relation.get_colour(), False, [(
                origin[0] + (point[0] * scale_x), origin[1] - (point[1] * scale_y)) for point in line], 2)

        return None

    # Return a pygame surface with a detailed graph, showing axis, intersects, and relations
    def create(self, func_domain, func_range, relations, offset, scale_x=25, scale_y=25) -> pygame.Surface:

        master_surface = pygame.Surface(self.size)

        # Get all possible values for the graphs domain and range
        all_x = [
            i / 100 for i in range(func_domain[0] * 100, (func_domain[1] * 100) + 1)]
        all_y = [
            i / 100 for i in range(func_range[0] * 100, (func_range[1] * 100) + 1)]
        
        # Get the centre of the graph
        origin = (self.plotting_size_x / 2, self.plotting_size_y / 2)

        # If the mouse is over a point, append a tooltip for that point
        tooltips = []
        if self.mode == self.TOOLTIP:

            # Get the mouse position relative to the graph surface, and the corresponding X/Y values
            mouse_x = pygame.mouse.get_pos()[0]
            mouse_y = pygame.mouse.get_pos()[1]
            relative_x_offset = abs(-(self.plotting_size_x / 2) +
                                    (self.size[0] / 2) + self.offset_x)
            relative_y_offset = abs(-(self.plotting_size_y / 2) +
                                    (self.size[1] / 2) + self.offset_y)
            relative_x = mouse_x - offset[0] + relative_x_offset
            relative_y = mouse_y - offset[1] + relative_y_offset
            x_val = round((relative_x - origin[0]) / scale_x, 2)
            y_val = round((origin[1] - relative_y) / scale_y, 2)

            # If the relative values are within the graph, generate a tooltip
            if relative_x_offset <= relative_x <= relative_x_offset + self.size[0] \
                and relative_y_offset <= relative_y <= relative_y_offset + self.size[1]:
                for eq in self.lines:
                    for line in self.lines[eq]:
                        for point in line:
                            # Only follow the relative X if the graph is dependant on Y, otherwise vice versa.
                            y_dependant_point = False if type(point[0]) != float else True
                            if y_dependant_point and point[0] == x_val:
                                y_display = round(float(point[1]), 2)
                                tooltips.append(
                                    [point[0], point[1], render_text("Line: --------", 14, color=eq.get_colour()),
                                     render_text(
                                         "X: " + str(x_val), 14, color=BLACK),
                                     render_text("Y: " + str(y_display), 14, color=BLACK), y_dependant_point])
                                continue
                            if not y_dependant_point and point[1] == y_val:
                                x_display = round(float(point[0]), 2)
                                tooltips.append(
                                    [point[0], point[1], render_text("Line: --------", 14, color=eq.get_colour()),
                                     render_text(
                                         "X: " + str(x_display), 14, color=BLACK),
                                     render_text("Y: " + str(y_val), 14, color=BLACK), y_dependant_point])
                                continue
        
        # Use cached graph if it hasn't changed. Otherwise, recalculate necessary changes
        if self.cache != {'func_domain': func_domain, 'func_range': func_range, 'scale_x': scale_x, 'scale_y': scale_y,
                          'offset_x': self.offset_x, 'offset_y': self.offset_y, 'relations': relations}:
            if len(range(0, func_domain[1])) > len(range(func_domain[0], 0)):
                plotting_size_x = (len(range(0, func_domain[1])) + 1) * 2 * scale_x
            else:
                plotting_size_x = (len(range(func_domain[0], 0)) + 1) * 2 * scale_x
            if plotting_size_x < self.size[0]:
                plotting_size_x = self.size[0]
            if len(range(0, func_range[1])) > len(range(func_range[0], 0)):
                plotting_size_y = (len(range(0, func_range[1])) + 1) * 2 * scale_y
            else:
                plotting_size_y = (len(range(func_range[0], 0)) + 1) * 2 * scale_y
            if plotting_size_y < self.size[1]:
                plotting_size_y = self.size[1]
            self.plotting_size_x = plotting_size_x
            self.plotting_size_y = plotting_size_y
        else:
            # Create a copy of the cached graph to draw on
            surf = self.last_surface.copy()

            # Draw each tooltip and a line pointing to it
            prev_rects = []
            x_accumulated = 0
            y_accumulated = 0
            for tooltip in tooltips:
                point_coordinate = (
                    origin[0] + int(tooltip[0] * scale_x), origin[1] - int(tooltip[1] * scale_y))
                pygame.draw.circle(surf, BLACK, point_coordinate, 2)
                rect = pygame.Rect(
                    point_coordinate[0] + 10 + x_accumulated, point_coordinate[1] + 10 + y_accumulated,
                    tooltip[2].get_width() + 15, 65)
                for i in prev_rects:
                    if rect.colliderect(i):
                        if tooltip[5]:
                            x_accumulated += i.width + 10
                        else:
                            y_accumulated += (i.height * 2) + 10
                rect.left = point_coordinate[0] + 10 + x_accumulated
                rect.top = point_coordinate[1] + 10 + y_accumulated
                pygame.draw.aaline(surf, BLACK, point_coordinate, (rect.left, rect.top))
                pygame.draw.rect(surf, WHITE, rect)
                surf.blit(tooltip[2], (point_coordinate[0] +
                                       15 + x_accumulated, point_coordinate[1] + 15 + y_accumulated))
                surf.blit(tooltip[3], (point_coordinate[0] +
                                       15 + x_accumulated, point_coordinate[1] + 35 + y_accumulated))
                surf.blit(tooltip[4], (point_coordinate[0] +
                                       15 + x_accumulated, point_coordinate[1] + 55 + y_accumulated))
                prev_rects.append(rect)

            # Draw the currently viewed portion of the graph, based on how offset from the origin it is
            master_surface.blit(
                surf, (-(self.plotting_size_x / 2) + (self.size[0] / 2) + self.offset_x,
                       -(self.plotting_size_y / 2) + (self.size[1] / 2) + self.offset_y))

            return master_surface

        # Define the total size of the graph (including what is not being currently viewed)
        overarching_size = (plotting_size_x, plotting_size_y)

        # Recalculate the centre of the graph
        origin = (plotting_size_x / 2, plotting_size_y / 2)
        
        # Define the coordinates of the surface which is currently being viewed
        viewport = (((plotting_size_x / 2) - self.offset_x) - (self.size[0] / 2),
                    ((plotting_size_y / 2) - self.offset_y) - (self.size[1] / 2))

        viewport_max = (((plotting_size_x / 2) - self.offset_x) - (self.size[0] / 2) + self.size[0],
                        ((plotting_size_y / 2) - self.offset_y) - (self.size[1] / 2) + self.size[1])

        # Create surface and fill background
        graph_surface = pygame.Surface(overarching_size)
        graph_surface.fill(BACKGROUND_GREY)

        # Draw X and Y axis
        pygame.draw.line(graph_surface, BLACK, (0,
                                                overarching_size[1] / 2),
                         (overarching_size[0], overarching_size[1] / 2))
        pygame.draw.line(
            graph_surface, BLACK, (overarching_size[0] / 2, 0), (overarching_size[0] / 2, overarching_size[1]))

        # Draw origin
        pygame.draw.circle(graph_surface, BLACK, origin, 3)
        graph_surface.blit(render_text("0", 10, color=DARK_GREY),
                           (origin[0] - 10, origin[1] + 4))

        # Draw X axis coordinates
        for num in range(func_domain[0], func_domain[1] + 1):
            # Draw multiples of 20 if the scale is very little
            if scale_x < 5 and num % 20 != 0:
                continue
            # Draw multiples of 5 if the scale is moderately low
            if scale_x < 15 and num % 5 != 0:
                continue
            # Draw half numbers if the scale is pretty high
            if scale_x > 75:
                half = num - 0.5
                if half > 0:
                    coordinate = (origin[0] + (scale_x * half), origin[1])
                    if in_viewport(coordinate, viewport, viewport_max):
                        pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                        graph_surface.blit(render_text(
                            str(half), 10, color=DARK_GREY), (coordinate[0] - 2, coordinate[1] + 7))
                if half < 0:
                    coordinate = (origin[0] - (scale_x * abs(half)), origin[1])
                    if in_viewport(coordinate, viewport, viewport_max):
                        pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                        graph_surface.blit(render_text(
                            str(half), 10, color=DARK_GREY), (coordinate[0] - 6, coordinate[1] + 7))
            # Draw all numbers that can currently be seen
            if num > 0:
                coordinate = (origin[0] + (scale_x * num), origin[1])
                if in_viewport(coordinate, viewport, viewport_max):
                    pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                    graph_surface.blit(render_text(
                        str(num), 10, color=DARK_GREY), (coordinate[0] - 2, coordinate[1] + 7))
            if num < 0:
                coordinate = (origin[0] - (scale_x * abs(num)), origin[1])
                if in_viewport(coordinate, viewport, viewport_max):
                    pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                    graph_surface.blit(render_text(
                        str(num), 10, color=DARK_GREY), (coordinate[0] - 6, coordinate[1] + 7))

        # Draw Y axis coordinates
        for num in range(func_range[0], func_range[1] + 1):
            # Draw multiples of 20 if the scale is very little
            if scale_y < 5 and num % 20 != 0:
                continue
            # Draw multiples of 5 if the scale is moderately low
            if scale_y < 15 and num % 5 != 0:
                continue
            # Draw half numbers if the scale is pretty high
            if scale_y > 75:
                half = num - 0.5
                if half > 0:
                    coordinate = (origin[0], origin[1] - (scale_y * half))
                    if in_viewport(coordinate, viewport, viewport_max):
                        pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                        text = render_text(str(half), 10, color=DARK_GREY)
                        graph_surface.blit(
                            text, (coordinate[0] - 12 - text.get_width(), coordinate[1] - 5))
                if half < 0:
                    coordinate = (origin[0], origin[1] + (scale_y * abs(half)))
                    if in_viewport(coordinate, viewport, viewport_max):
                        pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                        graph_surface.blit(render_text(
                            str(half), 10, color=DARK_GREY), (coordinate[0] + 8, coordinate[1] - 5))
            # Draw all numbers that can currently be seen
            if num > 0:
                coordinate = (origin[0], origin[1] - (scale_y * num))
                if in_viewport(coordinate, viewport, viewport_max):
                    pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                    text = render_text(str(num), 10, color=DARK_GREY)
                    graph_surface.blit(
                        text, (coordinate[0] - 12 - text.get_width(), coordinate[1] - 5))
            if num < 0:
                coordinate = (origin[0], origin[1] + (scale_y * abs(num)))
                if in_viewport(coordinate, viewport, viewport_max):
                    pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                    graph_surface.blit(render_text(
                        str(num), 10, color=DARK_GREY), (coordinate[0] + 8, coordinate[1] - 5))

        
        # Empty the cached points if the relations have changed or don't exist yet
        if 'relations' not in self.cache or self.cache['relations'] != relations:
            self.lines = {}
            self.alternate = {}

        # If the domain and range has changed, force regenerate the relation 
        changed_d_r = False
        if self.cache['func_domain'] != func_domain or self.cache['func_range'] != func_range:
            changed_d_r = True

        # Sketch relations and note if they are alternatively rendered
        low_res = []
        for relation in relations:
            sketch = self.sketch(all_x, all_y,
                                 relation, scale_x, scale_y, graph_surface, changed_d_r)
            if sketch is not None:
                low_res.append(sketch)

        # Send a low resolution warning containing all the low-res graphs
        if len(low_res) > 0:
            low_res_warning(low_res)

        # Draw the currently viewed portion of the graph, based on how offset from the origin it is
        master_surface.blit(
            graph_surface, (-(overarching_size[0] / 2) + (self.size[0] / 2) + self.offset_x,
                            -(overarching_size[1] / 2) + (self.size[1] / 2) + self.offset_y))

        # Cache the last graphed domain and range, scales, offsets and relations
        self.cache = {'func_domain': func_domain, 'func_range': func_range, 'scale_x': scale_x,
                      'scale_y': scale_y, 'offset_x': self.offset_x, 'offset_y': self.offset_y, 'relations': relations}

        # Cache the last graphed surfaces
        self.last_surface = graph_surface
        self.viewing_surface = master_surface

        return master_surface

    # Check for any clicks on the graph, its buttons, equation inputs and sliders
    def handle_changes(self, buttons_pressed, clicked) -> object:

        # Ensure the graph, when being rescaled, does not overshoot its size
        if self.offset_x > self.plotting_size_x / 2 - self.size[0] / 2:
            self.offset_x = self.plotting_size_x / 2 - self.size[0] / 2
        elif self.offset_x < -(self.plotting_size_x / 2 - self.size[0] / 2):
            self.offset_x = int(-(self.plotting_size_x / 2 - self.size[0] / 2))
        if self.offset_y > self.plotting_size_y / 2 - self.size[1] / 2:
            self.offset_y = self.plotting_size_y / 2 - self.size[1] / 2
        elif self.offset_y < -(self.plotting_size_y / 2 - self.size[1] / 2):
            self.offset_y = int(-(self.plotting_size_y / 2 - self.size[1] / 2))

        # Ensure only one object is recorded as clicked
        if clicked is None:

            # Check for any hovered objects and change the cursor type accordingly
            hovered = False
            for button in self.buttons:
                hovered = button.on_hover() if not hovered else True
                if hovered:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            for textbox in self.textboxes:
                if textbox.last_surface.get_rect(topleft=textbox.get_pos()).collidepoint(pygame.mouse.get_pos()):
                    hovered = True if not hovered else True
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            for textbox in self.d_r_boxes:
                if textbox.last_surface is not None:
                    if textbox.last_surface.get_rect(topleft=textbox.get_pos()).collidepoint(pygame.mouse.get_pos()):
                        hovered = True if not hovered else True
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            if self.viewing_surface.get_rect(topleft=self.get_pos()).collidepoint(pygame.mouse.get_pos()):
                if self.mode == self.PAN:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
                if self.mode == self.TOOLTIP:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
                hovered = True
            for slider in self.sliders:
                if slider.current_surface.get_rect(topleft=slider.get_pos()).collidepoint(pygame.mouse.get_pos()):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
                    slider.set_tooltip(True)
                    hovered = True
                else:
                    slider.set_tooltip(False)
            pygame.mouse.set_cursor(
                pygame.SYSTEM_CURSOR_ARROW) if not hovered else None

        # Offset the graph if it is in PAN mode
        if self.get_clicked() and self.mode == self.PAN:
            pygame.mouse.set_visible(False)
            last_pos = self.get_mouse_pos()
            self.shift_x(pygame.mouse.get_pos()[0] - last_pos[0])
            self.shift_y(pygame.mouse.get_pos()[1] - last_pos[1])
            self.set_clicked(True, pygame.mouse.get_pos())

        # Handle objects when the left mouse button is pressed
        if buttons_pressed[0]:

            # Set equation input active if it is clicked
            for textbox in self.textboxes:
                if textbox.last_surface is not None:
                    if textbox.last_surface.get_rect(topleft=textbox.get_pos()).collidepoint(pygame.mouse.get_pos()):
                        if clicked is None:
                            textbox.set_active(True)
                    else:
                        textbox.set_active(False)
            
            # Set domain/range input active if it is clicked
            for textbox in self.d_r_boxes:
                if textbox.last_surface is not None:
                    if textbox.last_surface.get_rect(topleft=textbox.get_pos()).collidepoint(pygame.mouse.get_pos()):
                        if clicked is None:
                            textbox.set_active(True)
                    else:
                        textbox.set_active(False)
            
            # If the slider or graph is clicked, set it as the clicked object 
            for slider in self.sliders:
                if slider == clicked or clicked is None:
                    if slider.current_surface.get_rect(topleft=slider.get_pos()).collidepoint(pygame.mouse.get_pos()):
                        slider.set_clicked(True)
                        clicked = slider
            if self == clicked or clicked is None:
                if self.viewing_surface.get_rect(topleft=self.get_pos()).collidepoint(pygame.mouse.get_pos()):
                    self.set_clicked(True, pygame.mouse.get_pos())
                    clicked = self
            
            # Otherwise process a button click
            if clicked is None:
                for button in self.buttons:
                    button.on_click()

        else:

            # Ensure all UX elements are reset to normal when nothing is clicked
            pygame.mouse.set_visible(True)
            clicked = None
            if self.get_clicked():
                self.set_clicked(False)
            for slider in self.sliders:
                if slider.get_clicked():
                    slider.set_clicked(False)

        # Ensure the sliders do not exceed their range
        for slider in self.sliders:
            if slider.get_clicked():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
                if pygame.mouse.get_pos()[0] <= slider.get_pos()[0] + slider.radius:
                    slider.current_x = slider.radius
                    continue
                if pygame.mouse.get_pos()[0] >= slider.get_pos()[0] + slider.size_x + slider.radius:
                    slider.current_x = slider.size_x + slider.radius
                    continue
                slider.current_x = pygame.mouse.get_pos()[
                                       0] - slider.get_pos()[0]

        return clicked

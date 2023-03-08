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

# Fonts
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
    'Oxanium-Regular.ttf', 'press-start.ttf'

FACTORIAL = sympify(sympy.sympify("factorial(x)"))

if getattr(sys, 'frozen', False):
    CurrentPath = sys._MEIPASS
else:
    CurrentPath = ''


# Returns a surface with text in the game font
def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    font = pygame.font.Font(os.path.join(
        CurrentPath, 'assets', 'fonts', font), px)
    text = font.render(text, False, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


def in_viewport(coordinate, viewport, viewport_max):
    return True if viewport[0] <= coordinate[0] <= viewport_max[0] and viewport[1] <= coordinate[1] <= viewport_max[
        1] else False


def low_res_warning(x):
    all_graphs = "\n   • ".join(x)
    warning = f"""The following graph(s) cannot be fully evaluated:\n   • {all_graphs}\nEvaluating at low resolution"""
    messagebox.showwarning("Warning", warning)


def multisolver(expression):
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
    x_exprs, y_exprs = relation.f()

    symbol_x = Symbol('x')
    symbol_y = Symbol('y')

    lines_to_draw = []

    for expr in y_exprs.args:

        if type(expr) == symengine.Pow:
            if type(expr.args[1]) == symengine.Rational:
                num, den = expr.args[1].get_num_den()
                real_root = sympify(
                    sympy.real_root(sympy.Pow(expr.args[0], num), den))
                expr = real_root
            else:
                expr = multisolver(expr)

        points = []
        for x_val in all_x:
            if factorial_checker(expr):
                if x_val < 0 and x_val % 1 == 0:
                    if len(points) > 1:
                        lines_to_draw.append(points)
                    points = []
                    continue
            y_val = expr.xreplace({symbol_x: x_val})
            try:
                y_val = symengine.Float(y_val)
            except RuntimeError:
                pass
            if not y_val.is_real:
                if len(points) > 1:
                    lines_to_draw.append(points)
                points = []
                continue
            if y_val < all_y[0] or y_val > all_y[-1]:
                if len(points) > 1:
                    lines_to_draw.append(points)
                points = []
                continue
            points.append((x_val, y_val))
        if len(points) > 1:
            lines_to_draw.append(points)

    if len(y_exprs.args) == 0:
        for expr in x_exprs.args:
            points = []
            for y_val in all_y:
                x_val = expr.xreplace({symbol_y: y_val})
                if not x_val.is_real:
                    if len(points) > 1:
                        lines_to_draw.append(points)
                    points = []
                    continue
                if x_val < all_x[0] or x_val > all_x[-1]:
                    if len(points) > 1:
                        lines_to_draw.append(points)
                    points = []
                    continue
                points.append((x_val, y_val))
            if len(points) > 1:
                lines_to_draw.append(points)

    alternate_renders = []

    if len(lines_to_draw) == 0:
        if relation.lhs != relation.rhs:
            alternate_renders = []
            for x_val in all_x:
                if not (x_val * 10).is_integer():
                    continue
                for y_val in all_y:
                    if not (y_val * 10).is_integer():
                        continue
                    ex = sympify(relation.lhs + " - " + relation.rhs)
                    ans = ex.xreplace(
                        {symbol_x: x_val, symbol_y: y_val})
                    if ans.is_real and -0.1 <= ans <= 0.1:
                        alternate_renders.append((x_val, y_val))

    return lines_to_draw, alternate_renders


class Graph:
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

    def extend(self, size_x) -> None:
        self.size = (size_x, self.size[1])

    def get_d_r_boxes(self) -> list:
        return self.d_r_boxes

    def add_textbox(self) -> None:
        random_colour = choice(
            [i for i in COLOURS if i not in self.used_colours])
        self.used_colours.append(random_colour)
        self.textboxes.append(
            Textbox((200, 30), 18, "Equation " + str(len(self.textboxes) + 1), random_colour))

    def remove_textbox(self, textbox) -> None:
        self.textboxes.remove(textbox)

    def get_textboxes(self) -> list:
        return self.textboxes

    def get_clicked(self) -> bool:
        return self.clicked

    def set_clicked(self, bool, mouse_pos=None) -> None:
        self.clicked = bool
        self.mouse_pos = mouse_pos

    def set_pos(self, pos) -> None:
        self.pos = pos

    def get_pos(self) -> tuple:
        return self.pos

    def set_mode(self, mode) -> None:
        self.mode = mode

    def get_mode(self) -> int:
        return self.mode

    def get_mouse_pos(self) -> tuple:
        return self.mouse_pos

    def get_sliders(self) -> list:
        return self.sliders

    def get_buttons(self) -> list:
        return self.buttons

    def add_clear_button(self) -> None:
        clear_btn = Button(os.path.join(
            CurrentPath, 'assets', 'textures', 'broom.png'), (50, 110), self.CLEAR_EVENT, -1, "Clear")
        self.buttons.append(clear_btn)

    def shift_x(self, val) -> None:
        if self.offset_x + val > self.plotting_size_x / 2 - self.size[0] / 2:
            self.offset_x = self.plotting_size_x / 2 - self.size[0] / 2
            return
        if self.offset_x + val < -(self.plotting_size_x / 2 - self.size[0] / 2):
            self.offset_x = int(-(self.plotting_size_x / 2 - self.size[0] / 2))
            return
        self.offset_x += val

    def shift_y(self, val) -> None:
        if self.offset_y + val > self.plotting_size_y / 2 - self.size[1] / 2:
            self.offset_y = self.plotting_size_y / 2 - self.size[1] / 2
            return
        if self.offset_y + val < -(self.plotting_size_y / 2 - self.size[1] / 2):
            self.offset_y = int(-(self.plotting_size_y / 2 - self.size[1] / 2))
            return
        self.offset_y += val

    def reset(self) -> None:
        self.offset_x, self.offset_y = 0, 0
        for slider in self.sliders:
            slider.reset()

    def sketch(self, all_x, all_y, relation, scale_x, scale_y, graph_surface, change) -> str | None:
        origin = (self.plotting_size_x / 2, self.plotting_size_y / 2)

        if (relation not in self.lines and relation not in self.alternate) or change:

            async_result = self.pool.apply_async(calculate_x_y, (relation, all_x, all_y,))

            lines_to_draw, alternate_renders = async_result.get()

            self.lines[relation] = lines_to_draw
            self.alternate[relation] = alternate_renders

            if len(alternate_renders) > 0:
                if len(self.lines[relation]) == 0 and relation in self.alternate:
                    for point in self.alternate[relation]:
                        pygame.draw.circle(
                            graph_surface, relation.get_colour(),
                            (origin[0] + (point[0] * scale_x), origin[1] - (point[1] * scale_y)), 1)
                return str(relation.get_expression())

        if len(self.lines[relation]) == 0 and relation in self.alternate:
            for point in self.alternate[relation]:
                pygame.draw.circle(
                    graph_surface, relation.get_colour(),
                    (origin[0] + (point[0] * scale_x), origin[1] - (point[1] * scale_y)), 1)

        for line in self.lines[relation]:
            pygame.draw.aalines(graph_surface, relation.get_colour(), False, [(
                origin[0] + (point[0] * scale_x), origin[1] - (point[1] * scale_y)) for point in line], 2)

        return None

    def create(self, func_domain, func_range, relations, offset, scale_x=25, scale_y=25) -> pygame.Surface:

        master_surface = pygame.Surface(self.size)

        all_x = [
            i / 100 for i in range(func_domain[0] * 100, (func_domain[1] * 100) + 1)]
        all_y = [
            i / 100 for i in range(func_range[0] * 100, (func_range[1] * 100) + 1)]

        origin = (self.plotting_size_x / 2, self.plotting_size_y / 2)

        tooltips = []
        if self.mode == self.TOOLTIP:
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

            if relative_x_offset <= relative_x <= relative_x_offset + self.size[
                0] and relative_y_offset <= relative_y <= relative_y_offset + self.size[1]:
                for eq in self.lines:
                    for line in self.lines[eq]:
                        for point in line:
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
            surf = self.last_surface.copy()

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

            master_surface.blit(
                surf, (-(self.plotting_size_x / 2) + (self.size[0] / 2) + self.offset_x,
                       -(self.plotting_size_y / 2) + (self.size[1] / 2) + self.offset_y))

            return master_surface

        overarching_size = (plotting_size_x, plotting_size_y)

        origin = (plotting_size_x / 2, plotting_size_y / 2)

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
            if scale_x < 5 and num % 20 != 0:
                continue
            if scale_x < 15 and num % 5 != 0:
                continue
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
            if scale_y < 5 and num % 20 != 0:
                continue
            if scale_y < 15 and num % 5 != 0:
                continue
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

        low_res = []

        if 'relations' not in self.cache or self.cache['relations'] != relations:
            self.lines = {}
            self.alternate = {}

        changed_d_r = False
        if self.cache['func_domain'] != func_domain or self.cache['func_range'] != func_range:
            changed_d_r = True

        # Sketch actual relations
        for relation in relations:
            sketch = self.sketch(all_x, all_y,
                                 relation, scale_x, scale_y, graph_surface, changed_d_r)
            if sketch is not None:
                low_res.append(sketch)

        if len(low_res) > 0:
            low_res_warning(low_res)

        master_surface.blit(
            graph_surface, (-(overarching_size[0] / 2) + (self.size[0] / 2) + self.offset_x,
                            -(overarching_size[1] / 2) + (self.size[1] / 2) + self.offset_y))

        self.cache = {'func_domain': func_domain, 'func_range': func_range, 'scale_x': scale_x,
                      'scale_y': scale_y, 'offset_x': self.offset_x, 'offset_y': self.offset_y, 'relations': relations}

        self.last_surface = graph_surface
        self.viewing_surface = master_surface
        return master_surface

    def handle_changes(self, buttons_pressed, clicked) -> object:

        if clicked is None:
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

        if self.get_clicked() and self.mode == self.PAN:
            pygame.mouse.set_visible(False)
            last_pos = self.get_mouse_pos()
            self.shift_x(pygame.mouse.get_pos()[0] - last_pos[0])
            self.shift_y(pygame.mouse.get_pos()[1] - last_pos[1])
            self.set_clicked(True, pygame.mouse.get_pos())

        if buttons_pressed[0]:
            for textbox in self.textboxes:
                if textbox.last_surface is not None:
                    if textbox.last_surface.get_rect(topleft=textbox.get_pos()).collidepoint(pygame.mouse.get_pos()):
                        if clicked is None:
                            textbox.set_active(True)
                    else:
                        textbox.set_active(False)
            for textbox in self.d_r_boxes:
                if textbox.last_surface is not None:
                    if textbox.last_surface.get_rect(topleft=textbox.get_pos()).collidepoint(pygame.mouse.get_pos()):
                        if clicked is None:
                            textbox.set_active(True)
                    else:
                        textbox.set_active(False)
            for slider in self.sliders:
                if slider == clicked or clicked is None:
                    if slider.current_surface.get_rect(topleft=slider.get_pos()).collidepoint(pygame.mouse.get_pos()):
                        slider.set_clicked(True)
                        clicked = slider
            if self == clicked or clicked is None:
                if self.viewing_surface.get_rect(topleft=self.get_pos()).collidepoint(pygame.mouse.get_pos()):
                    self.set_clicked(True, pygame.mouse.get_pos())
                    clicked = self
            if clicked is None:
                for button in self.buttons:
                    button.on_click()
        else:
            pygame.mouse.set_visible(True)
            clicked = None
            if self.get_clicked():
                self.set_clicked(False)
            for slider in self.sliders:
                if slider.get_clicked():
                    slider.set_clicked(False)

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

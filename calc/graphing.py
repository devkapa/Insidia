import os
import pygame
from symengine import Symbol
from widgets.slider import Slider


# RGB colour constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 207, 85)
PURPLE = (189, 145, 255)
RED = (255, 100, 128)
DARK_GREY = (100, 100, 100)
BACKGROUND_GREY = (239, 239, 239)

# Fonts
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
    'Oxanium-Regular.ttf', 'press-start.ttf'


# Returns a surface with text in the game font
def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    font = pygame.font.Font(os.path.join('assets', 'fonts', font), px)
    text = font.render(text, False, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


def dy_dx(func, x):
    h = 1e-5
    return (func(x+h) - func(x))/h


def in_viewport(coordinate, viewport, viewport_max):
    return True if coordinate[0] >= viewport[0] and coordinate[0] <= viewport_max[0] and coordinate[1] >= viewport[1] and coordinate[1] <= viewport_max[1] else False


def in_x_viewport(coordinate, viewport, viewport_max):
    return True if coordinate[0] >= viewport[0] and coordinate[0] <= viewport_max[0] else False


class Graph:

    formula: str
    size: tuple
    offset_x: int
    offset_y: int
    cache: dict
    last_surface: pygame.Surface
    viewing_surface: pygame.Surface
    pos: tuple
    mouse_pos: tuple
    clicked: bool
    sliders: list
    tooltips: list

    def __init__(self, formula, size) -> None:
        self.formula = formula
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
        self.sliders = [Slider(10, 100, 200, 10, 10, default=25),
                        Slider(10, 100, 200, 10, 10, default=25)]
        self.tooltips = []

    def get_clicked(self) -> bool:
        return self.clicked

    def set_clicked(self, bool, mouse_pos=None) -> None:
        self.clicked = bool
        self.mouse_pos = mouse_pos

    def set_pos(self, pos) -> None:
        self.pos = pos

    def get_pos(self) -> tuple:
        return self.pos

    def get_mouse_pos(self) -> tuple:
        return self.mouse_pos

    def get_sliders(self) -> list:
        return self.sliders

    def shift_x(self, val) -> None:
        if self.offset_x + val > self.plotting_size_x/2 - self.size[0]/2 or self.offset_x + val < -(self.plotting_size_x/2 - self.size[0]/2):
            return
        self.offset_x += val

    def shift_y(self, val) -> None:
        if self.offset_y + val > self.plotting_size_y/2 - self.size[1]/2 or self.offset_y + val < -(self.plotting_size_y/2 - self.size[1]/2):
            return
        self.offset_y += val

    def reset_offset(self) -> None:
        self.offset_x, self.offset_y = 0, 0

    def sketch(self, func_domain, func_range, relation, scale_x, scale_y, graph_surface, viewport, viewport_max) -> tuple:
        increment = 1
        origin = (self.plotting_size_x/2, self.plotting_size_y/2)
        minimum = origin[0] + (func_domain[0]*scale_x)
        maximum = origin[0] + (func_domain[1]*scale_x)
        x_sym = Symbol('x')
        y_values = relation.f()
        for point in y_values.args:
            points = []
            i = minimum
            while i <= maximum:
                x = (i-origin[0])/scale_x
                y = point.xreplace({x_sym: x})
                if not y.is_real:
                    if len(points) > 1:
                        pygame.draw.aalines(
                            graph_surface, BLACK, False, points, 2)
                    points = []
                    i += increment
                    continue
                real_y = origin[1] - (y*scale_y)
                scaled_range = (origin[1] + (func_range[0]*scale_y),
                                origin[1] + (func_range[1]*scale_y))
                if real_y < scaled_range[0] or real_y > scaled_range[1]:
                    if len(points) > 1:
                        pygame.draw.aalines(
                            graph_surface, BLACK, False, points, 2)
                    points = []
                    i += increment
                    continue
                if in_x_viewport((int(i), int(real_y)), viewport, viewport_max):
                    points.append((int(i), int(real_y)))
                i += increment
            if len(points) > 1:
                pygame.draw.aalines(graph_surface, BLACK, False, points, 2)

    def create(self, func_domain, func_range, relations, scale_x=25, scale_y=25) -> pygame.Surface:

        master_surface = pygame.Surface(self.size)

        if self.cache != {'func_domain': func_domain, 'func_range': func_range, 'scale_x': scale_x, 'scale_y': scale_y, 'offset_x': self.offset_x, 'offset_y': self.offset_y}:
            domain_size = len(range(func_domain[0], func_domain[1] + 1))
            range_size = len(range(func_range[0], func_range[1] + 1))
            plotting_size_x = (domain_size * 5) * scale_x
            plotting_size_y = (range_size * 5) * scale_y
            self.plotting_size_x = plotting_size_x
            self.plotting_size_y = plotting_size_y
        else:
            master_surface.blit(
                self.last_surface, (-(self.plotting_size_x/2) + (self.size[0]/2) + self.offset_x, -(self.plotting_size_y/2) + (self.size[1]/2) + self.offset_y))
            return master_surface

        overarching_size = (plotting_size_x, plotting_size_y)

        origin = (plotting_size_x/2, plotting_size_y/2)

        viewport = (((plotting_size_x/2)-self.offset_x)-(self.size[0]/2),
                    ((plotting_size_y/2)-self.offset_y)-(self.size[1]/2))

        viewport_max = (((plotting_size_x/2)-self.offset_x)-(self.size[0]/2)+self.size[0],
                        ((plotting_size_y/2)-self.offset_y)-(self.size[1]/2)+self.size[1])

        # Create surface and fill background
        graph_surface = pygame.Surface(overarching_size)
        graph_surface.fill(BACKGROUND_GREY)

        # Draw X and Y axis
        pygame.draw.line(graph_surface, BLACK, (0,
                         overarching_size[1]/2), (overarching_size[0], overarching_size[1]/2))
        pygame.draw.line(
            graph_surface, BLACK, (overarching_size[0]/2, 0), (overarching_size[0]/2, overarching_size[1]))

        # Draw origin
        pygame.draw.circle(graph_surface, BLACK, origin, 3)
        graph_surface.blit(render_text("0", 10, color=DARK_GREY),
                           (origin[0] - 10, origin[1] + 4))

        # Draw X axis coordinates
        for num in range(func_domain[0], func_domain[1] + 1):
            if scale_x < 15 and num % 5 != 0:
                continue
            if scale_x > 75:
                half = num / 2
                if half > 0:
                    coordinate = (origin[0] + (scale_x*half), origin[1])
                    if in_viewport(coordinate, viewport, viewport_max):
                        pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                        graph_surface.blit(render_text(
                            str(half), 10, color=DARK_GREY), (coordinate[0] - 2, coordinate[1] + 7))
                if half < 0:
                    coordinate = (origin[0] - (scale_x*abs(half)), origin[1])
                    if in_viewport(coordinate, viewport, viewport_max):
                        pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                        graph_surface.blit(render_text(
                            str(half), 10, color=DARK_GREY), (coordinate[0] - 6, coordinate[1] + 7))
            if num > 0:
                coordinate = (origin[0] + (scale_x*num), origin[1])
                if in_viewport(coordinate, viewport, viewport_max):
                    pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                    graph_surface.blit(render_text(
                        str(num), 10, color=DARK_GREY), (coordinate[0] - 2, coordinate[1] + 7))
            if num < 0:
                coordinate = (origin[0] - (scale_x*abs(num)), origin[1])
                if in_viewport(coordinate, viewport, viewport_max):
                    pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                    graph_surface.blit(render_text(
                        str(num), 10, color=DARK_GREY), (coordinate[0] - 6, coordinate[1] + 7))

        # Draw Y axis coordinates
        for num in range(func_range[0], func_range[1] + 1):
            if scale_y < 15 and num % 5 != 0:
                continue
            if scale_y > 75:
                half = num / 2
                if half > 0:
                    coordinate = (origin[0], origin[1] - (scale_y*half))
                    if in_viewport(coordinate, viewport, viewport_max):
                        pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                        graph_surface.blit(render_text(
                            str(half), 10, color=DARK_GREY), (coordinate[0] - 12, coordinate[1] - 5))
                if half < 0:
                    coordinate = (origin[0], origin[1] + (scale_y*abs(half)))
                    if in_viewport(coordinate, viewport, viewport_max):
                        pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                        graph_surface.blit(render_text(
                            str(half), 10, color=DARK_GREY), (coordinate[0] + 8, coordinate[1] - 5))
            if num > 0:
                coordinate = (origin[0], origin[1] - (scale_y*num))
                if in_viewport(coordinate, viewport, viewport_max):
                    pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                    graph_surface.blit(render_text(
                        str(num), 10, color=DARK_GREY), (coordinate[0] - 12, coordinate[1] - 5))
            if num < 0:
                coordinate = (origin[0], origin[1] + (scale_y*abs(num)))
                if in_viewport(coordinate, viewport, viewport_max):
                    pygame.draw.circle(graph_surface, BLACK, coordinate, 3)
                    graph_surface.blit(render_text(
                        str(num), 10, color=DARK_GREY), (coordinate[0] + 8, coordinate[1] - 5))

        # Sketch actual relations
        for relation in relations:
            self.tooltips = self.sketch(func_domain, func_range,
                                        relation, scale_x, scale_y, graph_surface, viewport, viewport_max)

        master_surface.blit(
            graph_surface, (-(overarching_size[0]/2) + (self.size[0]/2) + self.offset_x, -(overarching_size[1]/2) + (self.size[1]/2) + self.offset_y))

        self.cache = {'func_domain': func_domain, 'func_range': func_range, 'scale_x': scale_x,
                      'scale_y': scale_y, 'offset_x': self.offset_x, 'offset_y': self.offset_y}

        self.last_surface = graph_surface
        self.viewing_surface = master_surface

        return master_surface

    def handle_changes(self, buttons_pressed, clicked) -> object:
        if clicked == None:
            hovered = False
            if self.viewing_surface.get_rect(topleft=self.get_pos()).collidepoint(pygame.mouse.get_pos()):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
                hovered = True
            for slider in self.sliders:
                if slider.current_surface.get_rect(topleft=slider.get_pos()).collidepoint(pygame.mouse.get_pos()):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
                    hovered = True
            pygame.mouse.set_cursor(
                pygame.SYSTEM_CURSOR_ARROW) if not hovered else None

        if self.get_clicked():
            pygame.mouse.set_visible(False)
            last_pos = self.get_mouse_pos()
            self.shift_x(pygame.mouse.get_pos()[0] - last_pos[0])
            self.shift_y(pygame.mouse.get_pos()[1] - last_pos[1])
            self.set_clicked(True, pygame.mouse.get_pos())

        if buttons_pressed[0]:
            for slider in self.sliders:
                if slider == clicked or clicked == None:
                    if slider.current_surface.get_rect(topleft=slider.get_pos()).collidepoint(pygame.mouse.get_pos()):
                        slider.set_clicked(True)
                        clicked = slider
            if self == clicked or clicked == None:
                if self.viewing_surface.get_rect(topleft=self.get_pos()).collidepoint(pygame.mouse.get_pos()):
                    self.set_clicked(True, pygame.mouse.get_pos())
                    clicked = self
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

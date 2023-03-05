import pygame
import os
import sys


# RGB colour constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GREY = (200, 200, 200)
BACKGROUND_COLOUR = (14, 17, 23)
RED = (220, 0, 0)

# Fonts
TITLE, SUBHEADING, REGULAR, PRESS_START = 'Oxanium-Bold.ttf', 'Oxanium-Medium.ttf', \
    'Oxanium-Regular.ttf', 'press-start.ttf'


if getattr(sys, 'frozen', False):
    CurrentPath = sys._MEIPASS
else:
    CurrentPath = os.path.dirname(__file__)


# Returns a surface with text in the game font
def render_text(text, px, font=REGULAR, color=WHITE, alpha=None):
    font = pygame.font.Font(os.path.join(
        CurrentPath, 'assets', 'fonts', font), px)
    text = font.render(text, False, color)
    text.set_alpha(alpha) if alpha is not None else None
    return text


class Textbox:

    value: str
    px: int
    active: bool
    colour: tuple
    rect: pygame.Rect
    pos: tuple
    default: str
    last_surface: pygame.Surface
    cursor_pos: int
    valid: bool

    WHITELIST = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_CARET, pygame.K_ASTERISK, pygame.K_LEFTPAREN, pygame.K_RIGHTPAREN, pygame.K_PLUS, pygame.K_MINUS, pygame.K_SLASH, pygame.K_EQUALS, pygame.K_PERIOD, pygame.K_SPACE, pygame.K_a,
                 pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q, pygame.K_r, pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z]

    NUMBERS_ONLY = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                    pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_MINUS]

    ARROWS = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]

    def __init__(self, size, px, title, colour, default=None) -> None:
        self.size = size
        self.px = px
        self.value = "" if default is None else default
        self.default = default
        self.active = False
        self.title = title
        self.colour = colour
        self.pos = None
        self.last_surface = None
        self.cursor_pos = 0
        self.valid = True

    def get_pos(self) -> tuple:
        return self.pos

    def set_active(self, bool) -> None:
        self.cursor_pos = len(self.value)
        self.active = bool

    def create(self, surface, left, top) -> None:
        self.pos = (left, top)
        title_text = self.title if self.valid else self.title + " - INVALID"
        title = render_text(title_text, self.px,
                            color=RED if not self.valid else self.colour)
        textbox_surface = pygame.Surface((
            self.size[0], self.size[1] + title.get_height() + 5))
        textbox_surface.fill(BACKGROUND_COLOUR)
        textbox_surface.blit(title, (0, 0))
        self.rect = pygame.Rect(0, title.get_height() + 5,
                                self.size[0], self.size[1])
        pygame.draw.rect(
            textbox_surface, RED if not self.valid else WHITE if not self.active else LIGHT_GREY, self.rect)
        text_with_cursor = self.text_with_cursor()
        text = render_text(
            "".join(text_with_cursor), self.px, color=BLACK)
        if self.active and text.get_width() > self.size[0] and len(text_with_cursor[0]) > 0:
            cursor_and_following = render_text(
                "".join([text_with_cursor[1], text_with_cursor[2]]), self.px, color=BLACK)
            if cursor_and_following.get_width() > self.size[0]/2:
                new_text = "".join(
                    [text_with_cursor[0][-10:], text_with_cursor[1], text_with_cursor[2]])
                new_text = render_text(new_text, self.px, color=BLACK)
                textbox_surface.blit(
                    new_text, (5, title.get_height() + self.size[1] / 2))
            else:
                textbox_surface.blit(
                    text, (-(text.get_width() - self.size[0]), title.get_height() + self.size[1]/2))
        else:
            textbox_surface.blit(
                text, (5, title.get_height() + self.size[1]/2))
        self.last_surface = textbox_surface
        surface.blit(textbox_surface, (left, top))

    def add_text(self, key) -> None:
        self.value = self.value[:self.cursor_pos] + \
            key + self.value[self.cursor_pos:]
        self.cursor_pos += 1

    def backspace(self) -> None:
        if len(self.value[:self.cursor_pos]) > 0:
            self.value = self.value[:self.cursor_pos][:-
                                                      1] + self.value[self.cursor_pos:]
            self.cursor_pos -= 1

    def text_with_cursor(self):
        if self.active:
            return [self.value[:self.cursor_pos], "|", self.value[self.cursor_pos:]]
        else:
            return [self.value]

    def reset(self) -> None:
        self.value = ""

    def get_text(self) -> str:
        return self.value

    def get_colour(self) -> tuple:
        return self.colour

    def move_cursor(self, key) -> None:
        if key == pygame.K_LEFT:
            if self.cursor_pos - 1 >= 0:
                self.cursor_pos -= 1
        if key == pygame.K_RIGHT:
            if self.cursor_pos + 1 <= len(self.value):
                self.cursor_pos += 1
        if key == pygame.K_UP:
            self.cursor_pos = 0
        if key == pygame.K_DOWN:
            self.cursor_pos = len(self.value)

    def set_validity(self, bool) -> None:
        self.valid = bool

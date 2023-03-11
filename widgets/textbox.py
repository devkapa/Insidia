import pygame
from commons import render_text

# RGB colour constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GREY = (200, 200, 200)
GREY = (128, 128, 128)
BACKGROUND_COLOUR = (14, 17, 23)
RED = (220, 0, 0)


class Textbox:
    """
    The textbox structure allows for user input, which is frustratingly non-trivial in pygame.
    Allows for input text to be restricted/filtered, colour coding, titles and dynamic navigation 
    through long blocks of text using the keyboard.
    """
    value: str
    px: int
    active: bool
    colour: tuple
    rect: pygame.Rect
    pos: tuple | None
    default: str
    last_surface: pygame.Surface | None
    cursor_pos: int
    valid: bool
    message_shown: bool

    # Allowed keys that may be typed into the textbox
    WHITELIST = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
                 pygame.K_8, pygame.K_9, pygame.K_CARET, pygame.K_ASTERISK, pygame.K_LEFTPAREN, pygame.K_RIGHTPAREN,
                 pygame.K_PLUS, pygame.K_MINUS, pygame.K_SLASH, pygame.K_EQUALS, pygame.K_PERIOD, pygame.K_SPACE,
                 pygame.K_a,
                 pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i,
                 pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p, pygame.K_q,
                 pygame.K_r, pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y,
                 pygame.K_z]

    # Allowed keys that may be used to navigate the textbox
    ARROWS = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]

    # Initialise the Textbox as a barebones structure to be later drawn
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
        self.message_shown = False

    # Get the textbox's last known position 
    def get_pos(self) -> tuple:
        return self.pos

    # Set the textbox to allow text input
    def set_active(self, active) -> None:
        self.cursor_pos = len(self.value)
        self.active = active

    # Given a surface, draw on it the textbox and its value respective of the cursor
    def create(self, surface, left, top) -> None:
        
        # Cache current position
        self.pos = (left, top)

        # Render a readable title
        title_text = self.title if self.valid else self.title + " - INVALID"
        title = render_text(title_text, self.px,
                            color=RED if not self.valid else self.colour)
        title_shadow = render_text(title_text, self.px)

        # Prepare the surface everything will draw on
        textbox_surface = pygame.Surface((
            self.size[0], self.size[1] + title.get_height() + 5))
        textbox_surface.fill(BACKGROUND_COLOUR)

        # Draw the textbox and title onto the surface
        textbox_surface.blit(title_shadow, (1, 1))
        textbox_surface.blit(title, (0, 0))
        self.rect = pygame.Rect(0, title.get_height() + 5,
                                self.size[0], self.size[1])
        pygame.draw.rect(
            textbox_surface, RED if not self.valid else WHITE if not self.active else LIGHT_GREY, self.rect)
        
        # If the cursor is beyond half the size of the textbox, and the contained text is longer than the textbox size, 
        # then blit the text with an offset so that the cursor appears in the middle for a scrolling effect.  
        text_with_cursor = self.text_with_cursor()
        text = render_text(
            "".join(text_with_cursor), self.px, color=BLACK)
        if self.active and text.get_width() > self.size[0] and len(text_with_cursor[0]) > 0:
            cursor_and_following = render_text(
                "".join([text_with_cursor[1], text_with_cursor[2]]), self.px, color=BLACK)
            if cursor_and_following.get_width() > self.size[0] / 2:
                new_text = "".join(
                    [text_with_cursor[0][-10:], text_with_cursor[1], text_with_cursor[2]])
                new_text = render_text(new_text, self.px, color=BLACK)
                textbox_surface.blit(
                    new_text, (5, (title.get_height() + 5 + self.size[1] / 2) - new_text.get_height()/2))
            else:
                textbox_surface.blit(
                    text, (-(text.get_width() - self.size[0]),
                            (title.get_height() + 5 + self.size[1] / 2) - text.get_height()/2))
        else:
            if self.value == "" and not self.active:
                placeholder_text = render_text("Type an expression...", self.px, color=GREY)
                textbox_surface.blit(
                    placeholder_text, (5, (title.get_height() + 5 + self.size[1] / 2) - text.get_height()/2))
            else:
                textbox_surface.blit(
                    text, (5, (title.get_height() + 5 + self.size[1] / 2) - text.get_height()/2))
            
        # Cache the last known surface for efficiency
        self.last_surface = textbox_surface
        
        surface.blit(textbox_surface, (left, top))

    # Add the character to the value at the cursor position, and increment the cursor position
    def add_text(self, key) -> None:
        self.value = self.value[:self.cursor_pos] + \
                     key + self.value[self.cursor_pos:]
        self.cursor_pos += 1

    # If the cursor is in front of a key, delete that key
    def backspace(self) -> None:
        if len(self.value[:self.cursor_pos]) > 0:
            self.value = self.value[:self.cursor_pos][:-1] + self.value[self.cursor_pos:]
            self.cursor_pos -= 1

    # If the textbox is active, return the text with a vertical pole cursor
    def text_with_cursor(self):
        if self.active:
            return [self.value[:self.cursor_pos], "|", self.value[self.cursor_pos:]]
        else:
            return [self.value]

    # Empty the textbox stored text
    def reset(self) -> None:
        self.value = ""

    # Get the textbox stored text
    def get_text(self) -> str:
        return self.value

    # Get the textbox title colour
    def get_colour(self) -> tuple:
        return self.colour

    # Displace the cursor if a directional key was pressed
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

    # Set if the textbox is considered a valid equation
    def set_validity(self, valid) -> None:
        self.valid = valid

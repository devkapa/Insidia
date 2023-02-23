from symengine import Symbol
from symengine.lib.symengine_wrapper import solve


class Relation:

    equation: str
    colour: tuple

    def __init__(self, equation, colour) -> None:
        self.equation = equation
        self.colour = colour

    def get_expression(self) -> object:
        return self.equation

    def get_colour(self) -> tuple:
        return self.colour

    def f(self) -> int:
        y = Symbol("y")
        y_values = solve(self.get_expression(), y)
        return y_values

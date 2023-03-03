from symengine import Symbol, sympify, Eq
from sympy import solveset, EmptySet, ConditionSet


class Relation:

    equation: str
    colour: tuple
    x_values: object
    y_values: object
    rhs: str
    lhs: str

    def __init__(self, equation, colour) -> None:
        self.equality(equation)
        self.colour = colour
        x = Symbol('x')
        y = Symbol('y')

        try:
            self.x_values = sympify(solveset(self.get_expression(), x))
        except:
            self.x_values = EmptySet

        try:
            self.y_values = sympify(solveset(self.get_expression(), y))
        except:
            self.y_values = EmptySet

    def equality(self, expression: str) -> object:
        expression = expression.split("=")
        self.lhs = expression[0]
        self.rhs = expression[1]
        self.equation = Eq(sympify(self.lhs), sympify(self.rhs))

    def get_expression(self) -> object:
        return self.equation

    def get_colour(self) -> tuple:
        return self.colour

    def f(self) -> int:
        return self.x_values, self.y_values

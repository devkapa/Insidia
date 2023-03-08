from symengine import Symbol, sympify, Eq
from sympy import solveset, EmptySet
from sympy import sympify as sympyify


class Relation:

    equation: str
    colour: tuple
    x_values: object
    y_values: object
    rhs: str
    lhs: str
    original_str: str

    def __init__(self, equation, colour) -> None:
        self.equality(equation)
        self.colour = colour
        self.original_str = equation
        x = Symbol('x')
        y = Symbol('y')

        try:
            self.y_values = sympify(solveset(self.get_expression(), y))
            self.x_values = EmptySet
        except:
            self.y_values = EmptySet

        if len(self.y_values.args) == 0:
            try:
                self.x_values = sympify(solveset(self.get_expression(), x))
            except:
                self.x_values = EmptySet

    def get_original(self) -> str:
        return self.original_str

    def equality(self, expression: str):
        expression = expression.split("=")
        if len(expression) != 2:
            raise Exception
        self.lhs = expression[0]
        self.rhs = expression[1]
        self.equation = Eq(sympyify(self.lhs), sympyify(self.rhs))

    def get_expression(self) -> object:
        return self.equation

    def get_colour(self) -> tuple:
        return self.colour

    def f(self) -> int:
        return self.x_values, self.y_values

from symengine import Symbol, sympify, Eq, SympifyError
from sympy import solveset, EmptySet, E
from sympy import sympify as sympyify
from sympy import SympifyError as SympyifyError


class RelationError(Exception):
    """Raised if there is an error in creating a Relation."""
    pass


class Relation:
    """
    The relation structure allows for the digital symbolic representation of a mathematical expression.
    It can convert strings to the python symbolic mathematics engine, sympy. This is where the bulk of solving occurs!
    Solutions for X and Y are calculated using symengine, a wrapper of a drop-in C++ replacement for sympy.
    """
    equation: Eq
    colour: tuple
    x_values: object
    y_values: object
    rhs: str
    lhs: str
    original_str: str

    # When initialised, do the bulk of the mathematics
    def __init__(self, equation, colour) -> None:

        # Create an equality from the string expression provided
        self.equality(equation)
        self.colour = colour
        self.original_str = equation
        x = Symbol('x')
        y = Symbol('y')

        # Attempt to solve for Y. If unsuccessful, or no solutions, try for X.
        try:
            self.y_values = sympify(solveset(self.get_expression(), y))
            self.x_values = EmptySet
        except (NotImplementedError, ValueError, SympifyError, TypeError):
            self.y_values = EmptySet

        if len(self.y_values.args) == 0:
            try:
                self.x_values = sympify(solveset(self.get_expression(), x))
            except (NotImplementedError, ValueError, SympifyError, TypeError):
                self.x_values = EmptySet

    # Get the unaltered original string expression passed during initialisation
    def get_original(self) -> str:
        return self.original_str

    # Create a valid equality that can later be solved
    def equality(self, expression: str):
        expression = expression.split("=")
        if len(expression) not in [1, 2]:
            raise RelationError
        if len(expression) == 1:
            self.lhs = "y"
            self.rhs = expression[0]
        else:
            self.lhs = expression[0]
            self.rhs = expression[1]
        sympy_locals = {"e": E, "Y": Symbol('y'), "X": Symbol('x')}
        try:
            self.equation = Eq(sympyify(self.lhs, locals=sympy_locals), sympyify(self.rhs, locals=sympy_locals))
        except (NotImplementedError, ValueError, SympyifyError, TypeError):
            raise RelationError

    # Return the digital symbolic expression 
    def get_expression(self) -> object:
        return self.equation

    # Return the RGB colour code to graph in
    def get_colour(self) -> tuple:
        return self.colour

    # Return the functions of x and y. f(x), f(y)
    def f(self) -> tuple:
        return self.x_values, self.y_values

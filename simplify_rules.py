from itertools import chain
from math import isclose, prod
from math_objects import *

class Simplify:
    """Class for simplification rules"""

    def __init__(self, pattern, result):
        self.pattern = pattern
        self.result = result
    
    def __repr__(self):
        return f"Simplify({self.pattern} -> {self.result})"

rules_syntax = (
    # Make constants integer whenever possible
    Simplify(lambda t: isinstance(t, Const) and isinstance(t.value, float) and isclose(t.value, round(t.value)),
             lambda t: Const(round(t.value))),
    # Replace empty Add and Mul
    Simplify(Add(), Const(0)), Simplify(Mul(), Const(1)),
    # Replace single-argument Add and Mul
    Simplify(Add(Unk('X')), Unk('X')), Simplify(Mul(Unk('X')), Unk('X')),
)

rules_eval = (
    # Error cases
    Simplify(Unk('X') / 0, Exception("X/0 encountered")),
    Simplify(Pow(0, 0), Exception("0^0 encountered")),
    Simplify(Root(Unk('X'), 0), Exception("X^(1/0) encountered")),
    # Addition with 0
    Simplify(lambda t: t.isinstance_add() and Const(0) in t.args,
             lambda t: Add(*(arg for arg in t.args if arg != Const(0)))),
    Simplify(Unk('X') - 0, Unk('X')),
    # Multiplication with 0
    Simplify(lambda t: t.isinstance_mul() and Const(0) in t.args, Const(0)),
    Simplify(0 / Unk('X'), Const(0)),
    # Multiplication with 1
    Simplify(lambda t: t.isinstance_mul() and Const(1) in t.args,
             lambda t: Mul(*(arg for arg in t.args if arg != Const(1)))),
    Simplify(Unk('X') / 1, Unk('X')),
    # Trivial powers
    Simplify(Pow(0, Unk('X')), Const(0)), ############################################################### This is buggy, because 0^-1 != 0
    Simplify(Pow(1, Unk('X')), Const(1)),
    Simplify(Pow(Unk('X'), 0), Const(1)),
    Simplify(Pow(Unk('X'), 1), Unk('X')),
    Simplify(Root(0, Unk('X')), Const(0)), ############################################################### This is buggy, because 0^(1/-1) != 0
    Simplify(Root(1, Unk('X')), Const(1)), ############################################################### This is buggy, because 1^(1/0) != 1
    Simplify(Root(Unk('X'), 1), Unk('X')),
    # Evaluate operations on constants
    Simplify(lambda t: t.isinstance_add() and sum(isinstance(arg, Const) for arg in t.args) >= 2,
             lambda t: Add(*(arg for arg in t.args if not isinstance(arg, Const)),
                           Const(sum(arg.value for arg in t.args if isinstance(arg, Const))))),
    Simplify(Unk_Const('X') - Unk_Const('Y'), lambda t: Const(t.args[0].value - t.args[1].value)),
    Simplify(lambda t: t.isinstance_mul() and sum(isinstance(arg, Const) for arg in t.args) >= 2,
             lambda t: Mul(Const(prod(arg.value for arg in t.args if isinstance(arg, Const))),
                           *(arg for arg in t.args if not isinstance(arg, Const)))),
    Simplify(Unk_Const('X') / Unk_Const('Y'), lambda t: Const(t.args[0].value / t.args[1].value)),
    Simplify(Pow(Unk_Const('X'), Unk_Const('Y')), lambda t: Const(t.args[0].value ** t.args[1].value)),
    Simplify(Root(Unk_Const('X'), Unk_Const('Y')), lambda t: Const(t.args[0].value ** (1/t.args[1].value))),
)

rules_nest = (
    # Nested addition
    Simplify(lambda t: t.isinstance_add() and any(arg.isinstance_add() for arg in t.args),
             lambda t: Add(*chain.from_iterable(arg.args if arg.isinstance_add() else [arg] for arg in t.args))),
    # Subtraction under addition
    Simplify(lambda t: t.isinstance_add() and any(arg.isinstance_sub() for arg in t.args),
             lambda t: Sub(Add(*(arg.args[0] if arg.isinstance_sub() else arg for arg in t.args)),
                           Add(*(arg.args[1] for arg in t.args if arg.isinstance_sub())))),
    # Nested subtraction
    Simplify((Unk('X') - Unk('Y')) - Unk('Z'), Unk('X') - (Unk('Y') + Unk('Z'))),
    Simplify(Unk('X') - (Unk('Y') - Unk('Z')), (Unk('X') + Unk('Z')) - Unk('Y')),
    # Nested multiplication
    Simplify(lambda t: t.isinstance_mul() and any(arg.isinstance_mul() for arg in t.args),
             lambda t: Mul(*chain.from_iterable(arg.args if arg.isinstance_mul() else [arg] for arg in t.args))),
    # Division under multiplication
    Simplify(lambda t: t.isinstance_mul() and any(arg.isinstance_div() for arg in t.args),
             lambda t: Div(Mul(*(arg.args[0] if arg.isinstance_div() else arg for arg in t.args)),
                           Mul(*(arg.args[1] for arg in t.args if arg.isinstance_div())))),
    # Nested division
    Simplify((Unk('X') / Unk('Y')) / Unk('Z'), Unk('X') / (Unk('Y') * Unk('Z'))),
    Simplify(Unk('X') / (Unk('Y') / Unk('Z')), (Unk('X') * Unk('Z')) / Unk('Y')),
    # Double power
    Simplify((Unk('X') ** Unk('Y')) ** Unk('Z'), Unk('X') ** (Unk('Y') * Unk('Z'))),
    Simplify(Root(Unk('X'), Unk('Y')) ** Unk('Z'), Unk('X') ** (Unk('Z') / Unk('Y'))),
    Simplify(Root(Unk('X') ** Unk('Y'), Unk('Z')), Unk('X') ** (Unk('Y') / Unk('Z'))),
    Simplify(Root(Root(Unk('X'), Unk('Y')), Unk('Z')), Root(Unk('X'), Unk('Y') * Unk('Z'))),
)

simplify_rules_all = rules_syntax + rules_eval + rules_nest

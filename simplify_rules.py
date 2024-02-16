from itertools import chain
from math import isclose, prod
from nodes import *

class Rule:
    """Class for pattern rules"""

    def __init__(self, pattern, result):
        self.pattern = pattern
        self.result = result
    
    def __repr__(self):
        return f"Rule({self.pattern} -> {self.result})"

rules_syntax = (
    # Make constants integer whenever possible
    Rule(lambda t: isinstance(t, Const) and isinstance(t.value, float) and isclose(t.value, round(t.value)),
         lambda t: Const(round(t.value))),
    # Replace empty Add and Mul
    Rule(Add(), Const(0)), Rule(Mul(), Const(1)),
    # Replace single-argument Add and Mul
    Rule(Add(Unk('X')), Unk('X')), Rule(Mul(Unk('X')), Unk('X')),
)

rules_eval = (
    # Error cases
    Rule(Unk('X') / 0, Exception("X/0 encountered")),
    Rule(Pow(0, 0), Exception("0^0 encountered")),
    Rule(Root(Unk('X'), 0), Exception("X^(1/0) encountered")),
    # Addition with 0
    Rule(lambda t: t.isinstance_add() and Const(0) in t.args,
         lambda t: Add(*(arg for arg in t.args if arg != Const(0)))),
    Rule(Unk('X') - 0, Unk('X')),
    # Multiplication with 0
    Rule(lambda t: t.isinstance_mul() and Const(0) in t.args, Const(0)),
    Rule(0 / Unk('X'), Const(0)),
    # Multiplication with 1
    Rule(lambda t: t.isinstance_mul() and Const(1) in t.args,
         lambda t: Mul(*(arg for arg in t.args if arg != Const(1)))),
    Rule(Unk('X') / 1, Unk('X')),
    # Trivial powers
    Rule(Pow(0, Unk('X')), Const(0)),
    Rule(Pow(1, Unk('X')), Const(1)),
    Rule(Pow(Unk('X'), 0), Const(1)),
    Rule(Pow(Unk('X'), 1), Unk('X')),
    Rule(Root(0, Unk('X')), Const(0)),
    Rule(Root(1, Unk('X')), Const(1)),
    Rule(Root(Unk('X'), 1), Unk('X')),
    # Evaluate operations on constants
    Rule(lambda t: t.isinstance_add() and sum(isinstance(arg, Const) for arg in t.args) >= 2,
         lambda t: Add(*(arg for arg in t.args if not isinstance(arg, Const)),
                       Const(sum(arg.value for arg in t.args if isinstance(arg, Const))))),
    Rule(Unk_Const('X') - Unk_Const('Y'), lambda t: Const(t.args[0].value - t.args[1].value)),
    Rule(lambda t: t.isinstance_mul() and sum(isinstance(arg, Const) for arg in t.args) >= 2,
         lambda t: Mul(Const(prod(arg.value for arg in t.args if isinstance(arg, Const))),
                       *(arg for arg in t.args if not isinstance(arg, Const)))),
    Rule(Unk_Const('X') / Unk_Const('Y'), lambda t: Const(t.args[0].value / t.args[1].value)),
    Rule(Pow(Unk_Const('X'), Unk_Const('Y')), lambda t: Const(t.args[0].value ** t.args[1].value)),
    Rule(Root(Unk_Const('X'), Unk_Const('Y')), lambda t: Const(t.args[0].value ** (1/t.args[1].value))),
)

rules_nest = (
    # Nested addition
    Rule(lambda t: t.isinstance_add() and any(arg.isinstance_add() for arg in t.args),
         lambda t: Add(*chain.from_iterable(arg.args if arg.isinstance_add() else [arg] for arg in t.args))),
    # Subtraction under addition
    Rule(lambda t: t.isinstance_add() and any(arg.isinstance_sub() for arg in t.args),
         lambda t: Sub(Add(*(arg.args[0] if arg.isinstance_sub() else arg for arg in t.args)),
                       Add(*(arg.args[1] for arg in t.args if arg.isinstance_sub())))),
    # Nested subtraction
    Rule((Unk('X') - Unk('Y')) - Unk('Z'), Unk('X') - (Unk('Y') + Unk('Z'))),
    Rule(Unk('X') - (Unk('Y') - Unk('Z')), (Unk('X') + Unk('Z')) - Unk('Y')),
    # Nested multiplication
    Rule(lambda t: t.isinstance_mul() and any(arg.isinstance_mul() for arg in t.args),
         lambda t: Mul(*chain.from_iterable(arg.args if arg.isinstance_mul() else [arg] for arg in t.args))),
    # Division under multiplication
    Rule(lambda t: t.isinstance_mul() and any(arg.isinstance_div() for arg in t.args),
         lambda t: Div(Mul(*(arg.args[0] if arg.isinstance_div() else arg for arg in t.args)),
                       Mul(*(arg.args[1] for arg in t.args if arg.isinstance_div())))),
    # Nested division
    Rule((Unk('X') / Unk('Y')) / Unk('Z'), Unk('X') / (Unk('Y') * Unk('Z'))),
    Rule(Unk('X') / (Unk('Y') / Unk('Z')), (Unk('X') * Unk('Z')) / Unk('Y')),
    # Double power
    Rule((Unk('X') ** Unk('Y')) ** Unk('Z'), Unk('X') ** (Unk('Y') * Unk('Z'))),
    Rule(Root(Unk('X'), Unk('Y')) ** Unk('Z'), Unk('X') ** (Unk('Z') / Unk('Y'))),
    Rule(Root(Unk('X') ** Unk('Y'), Unk('Z')), Unk('X') ** (Unk('Y') / Unk('Z'))),
    Rule(Root(Root(Unk('X'), Unk('Y')), Unk('Z')), Root(Unk('X'), Unk('Y') * Unk('Z'))),
)

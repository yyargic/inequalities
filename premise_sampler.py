from random import choices
from math_objects import *
from simplify import simplify

def sample_terms(vars: list[Var], num_iter=1):

    consts = [Const(1)]
    terms = consts + vars
    weights = [10] * len(terms)
    powers = [Const(2), Const(3)]
    ops = ('Add', 'Sub', 'Mul', 'Div', 'Pow', 'Root')
    ops_weights = (4, 1, 4, 2, 1, 1)
    addmul_length = (2, 3)
    addmul_length_weights = (2, 1)
    for _ in range(num_iter):
        op = choices(ops, weights=ops_weights)[0]
        if op in ('Add', 'Mul'):
            length = choices(addmul_length, weights=addmul_length_weights)[0]
            args = choices(terms, weights=weights, k=length)
        elif op in ('Sub', 'Div'):
            args = choices(terms, weights=weights, k=2)
        elif op in ('Pow', 'Root'):
            args = choices(terms, weights=weights, k=1) + choices(powers, k=1)
        term = Op(op, *args)
        try:
            term = simplify(term)
        except:
            continue
        if (term not in terms) and term.hasvar():
            terms.append(term)
            weights.append(10)
    for term in terms:
        print(term)

sample_terms([Var('a'), Var('b'), Var('c')], 10)

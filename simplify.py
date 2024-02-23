from types import FunctionType
from math_objects import *
from pattern_match import pattern_match, substitute
from simplify_rules import Simplify

def simplify_by_rules(term, rules):
    """Apply a list of rules repeatedly until no more change"""
    if isinstance(rules, Simplify):
        return simplify_by_rules(term, [rules])
    assert isinstance(term, Term) and isinstance(rules, (tuple, list)) and all(isinstance(rule, Simplify) for rule in rules), "apply_rules(term, rules) takes term:Term and rules:list[Rule]"
    term, changed = _simplify_by_rules_once(term, rules)
    while changed:
        term, changed = _simplify_by_rules_once(term, rules)
    return term

def _simplify_by_rules_once(term, rules):
    """Apply a list of rules until the first change"""
    for rule in rules:
        subst = pattern_match(term, rule.pattern)
        if subst is not None:
            if isinstance(rule.result, Term):
                return substitute(rule.result, subst), True
            elif isinstance(rule.result, FunctionType):
                return substitute(rule.result(term), subst), True
            elif isinstance(rule.result, Exception):
                raise rule.result
            else:
                raise TypeError
    if isinstance(term, Op):
        arg_return = tuple(_simplify_by_rules_once(arg, rules) for arg in term.args)
        arg_return_args = tuple(arg for arg, _ in arg_return)
        arg_return_bool = any(changed for _, changed in arg_return)
        return Op(term.ftype, *arg_return_args), arg_return_bool
    return term, False

from simplify_rules import simplify_rules_all
def simplify(term):
    return simplify_by_rules(term, simplify_rules_all)

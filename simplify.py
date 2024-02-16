from types import FunctionType
from nodes import *
from simplify_rules import *

def pattern_match(term, pattern, subst={}):
    """Pattern matching, returns the substitution dictionary"""

    assert not isinstance(term, Unk), "The first term in pattern_match must not contain Unk instances"
    if subst is None:
        return None
    if isinstance(pattern, FunctionType):
        if pattern(term):
            return subst
        else:
            return None
    if term == pattern:
        return subst
    if isinstance(pattern, Unk):
        if pattern.name in subst:
            return pattern_match(term, subst[pattern.name], subst)
        if isinstance(pattern, Unk_Const):
            if isinstance(term, Const):
                return {**subst, pattern.name: term}
            else:
                return None
        else:
            return {**subst, pattern.name: term}
    if isinstance(term, Op) and isinstance(pattern, Op):
        if term.ftype != pattern.ftype:
            return None
        if term.ftype_group == 0: # Here, we treat Add and Mul as taking at most 2 ordered arguments
            if len(term.args) == 0 or len(pattern.args) == 0:
                if len(term.args) == 0 and len(pattern.args) == 0:
                    return subst
                else:
                    return None
            if len(term.args) == 1 or len(pattern.args) == 1:
                if len(term.args) == 1 and len(pattern.args) == 1:
                    return pattern_match(term.args[0], pattern.args[0], subst)
                else:
                    return None
            subst = pattern_match(term.args[-1], pattern.args[-1], subst)
            new_term = term.args[0] if len(term.args) == 2 else Op(term.ftype, *term.args[:-1])
            new_pattern = pattern.args[0] if len(pattern.args) == 2 else Op(pattern.ftype, *pattern.args[:-1])
            return pattern_match(new_term, new_pattern, subst)
        else:
            for term_arg, pattern_arg in zip(term.args, pattern.args):
                subst = pattern_match(term_arg, pattern_arg, subst)
            return subst
    return None

def substitute(term, subst):
    if subst == {}:
        return term
    if isinstance(term, Unk) and term.name in subst:
        return subst[term.name]
    if isinstance(term, Op):
        return Op(term.ftype, *(substitute(arg, subst) for arg in term.args))
    return term

def _apply_rules_once(term, rules):
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
        arg_return = tuple(_apply_rules_once(arg, rules) for arg in term.args)
        arg_return_args = tuple(arg for arg, _ in arg_return)
        arg_return_bool = any(changed for _, changed in arg_return)
        return Op(term.ftype, *arg_return_args), arg_return_bool
    return term, False

def apply_rules(term, rules):
    """Apply a list of rules repeatedly until no more change"""
    if isinstance(rules, Rule):
        return apply_rules(term, [rules])
    assert isinstance(term, Term) and isinstance(rules, (tuple, list)) and all(isinstance(rule, Rule) for rule in rules), "apply_rules(term, rules) takes term:Term and rules:list[Rule]"
    term, changed = _apply_rules_once(term, rules)
    while changed:
        term, changed = _apply_rules_once(term, rules)
    return term

def simplify(term):
    return apply_rules(term, rules_syntax + rules_eval + rules_nest)

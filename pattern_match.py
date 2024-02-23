from types import FunctionType
from math_objects import *

def pattern_match(object: Prop | Term, pattern: Prop | Term | FunctionType, subst=0):
    """Pattern matching for propositions and terms, returns the substitution dictionary"""

    assert isinstance(object, (Prop, Term)), "The object in pattern_match() must be Prop or Term"
    if subst == 0: # immutable default
        subst = {}
    if isinstance(object, Prop):
        assert isinstance(pattern, Prop), "The pattern in pattern_match() must be Prop"
        return _pattern_match_prop(object, pattern, subst)
    if isinstance(object, Term):
        assert isinstance(pattern, (Term, FunctionType)), "The pattern in pattern_match() must be Term or boolean function"
        return _pattern_match_term(object, pattern, subst)

def _pattern_match_prop(prop: Prop, pattern: Prop, subst):
    """Pattern matching for propositions, returns the substitution dictionary"""

    if prop.__class__ != pattern.__class__:
        return None
    subst = _pattern_match_term(prop.lhs, pattern.lhs, subst)
    subst = _pattern_match_term(prop.rhs, pattern.rhs, subst)
    return subst

def _pattern_match_term(term: Term, pattern: Term | FunctionType, subst):
    """Pattern matching for terms, returns the substitution dictionary"""

    assert not isinstance(term, Unk), "The term in _pattern_match_term() must not contain Unk instances"
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
            return _pattern_match_term(term, subst[pattern.name], subst)
        if isinstance(pattern, Unk_Const):
            if term.isconst():
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
                    return _pattern_match_term(term.args[0], pattern.args[0], subst)
                else:
                    return None
            subst = _pattern_match_term(term.args[-1], pattern.args[-1], subst)
            new_term = term.args[0] if len(term.args) == 2 else Op(term.ftype, *term.args[:-1])
            new_pattern = pattern.args[0] if len(pattern.args) == 2 else Op(pattern.ftype, *pattern.args[:-1])
            return _pattern_match_term(new_term, new_pattern, subst)
        else:
            for term_arg, pattern_arg in zip(term.args, pattern.args):
                subst = _pattern_match_term(term_arg, pattern_arg, subst)
            return subst
    return None

def substitute(object: Prop | Term, subst):
    """Substitutes the Unk instances in propositions and terms according to a dictionary"""

    if isinstance(object, Prop):
        return object.__class__(substitute(object.lhs, subst), substitute(object.rhs, subst))
    if subst == {}:
        return object
    if isinstance(object, Unk) and object.name in subst:
        return subst[object.name]
    if isinstance(object, Op):
        return Op(object.ftype, *(substitute(arg, subst) for arg in object.args))
    return object

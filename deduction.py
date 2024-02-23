from math_objects import *
from pattern_match import pattern_match, substitute
from simplify import simplify
from deduction_rules import Deduce, deduction_rules

def deduce(sol, rules=deduction_rules):
    changed = False
    for rule_name, rule in rules.items():
        changed_here = _deduce_once(sol, rule_name, rule)
        changed = changed or changed_here
    if changed:
        deduce(sol, rules)

def _deduce_once(sol, rule_name: str, rule: Deduce):
    substs_matching_assumptions = _assumption_match(sol.facts, rule.assumptions)
    for subst_m_a in substs_matching_assumptions:
        rule_matching_assumptions = substitute(rule.statement, subst_m_a)
        substs_matching_terms = _term_match(sol.terms, rule_matching_assumptions)
        for subst_m_t in substs_matching_terms:
            derived_statement = substitute(rule_matching_assumptions, subst_m_t)
            derived_statement = derived_statement.__class__(simplify(derived_statement.lhs), simplify(derived_statement.rhs))
            deduced = sol.add_fact(derived_statement, f"deduced by {rule_name}: {derived_statement}")
            if deduced:
                return True
    return False

def _term_match(terms: list[Term], statement: Prop):
    subst_list = [{}]
    if not statement.lhs.isconst():
        subst_list = _term_match_side(terms, statement.lhs, subst_list)
    if not statement.rhs.isconst():
        subst_list = _term_match_side(terms, statement.rhs, subst_list)
    return subst_list

def _term_match_side(terms: list[Term], statement_side: Prop, subst_list: list[dict]):
    new_subst_list = []
    for subst in subst_list:
        for term in terms:
            new_subst = pattern_match(term, statement_side, subst)
            if (new_subst is not None) and (new_subst not in new_subst_list):
                new_subst_list.append(new_subst)
    return new_subst_list

def _assumption_match(facts: list[Prop], assumptions: list[Prop]):
    subst_list = [{}]
    for assumption in assumptions:
        new_subst_list = []
        for subst in subst_list:
            for fact in facts:
                new_subst = pattern_match(fact, assumption, subst)
                if new_subst is not None:
                    new_subst_list.append(new_subst)
                if isinstance(fact, Eq):
                    new_subst = pattern_match(fact.rev(), assumption, subst)
                    if new_subst is not None:
                        new_subst_list.append(new_subst)
        subst_list = new_subst_list
    return subst_list

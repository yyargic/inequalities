from nodes import *

class Problem:
    """Problem statement"""

    def __init__(self, goal: Le, *assumptions: Prop):
        assert isinstance(goal, Le), "Problem.__init__(goal, *assumptions) takes Le for goal"
        assert all(isinstance(assumption, (Le, Eq)) for assumption in assumptions), "Problem.__init__(goal, *assumptions) takes Le or Eq for assumptions"
        assert not goal.hasunk(), "The goal must not contain Unk instances"
        assert goal.hasvar(), "The goal must contain at least one variable"
        assert not any(assumption.hasunk() for assumption in assumptions), "The assumptions must not contain Unk instances"
        assert all(assumption.hasvar() for assumption in assumptions), "The assumptions must contain at least one variable"
        self.goal = goal
        self.assumptions = assumptions
        self.vars = set(var.name for var in goal if isinstance(var, Var))
        self.vars = tuple(sorted(Var(name) for name in self.vars))
        assert all(var in self.vars for assumption in assumptions for var in assumption if isinstance(var, Var)), "The assumptions must not contain variables that are not in the goal"

    def __str__(self):
        out = '\033[4m' + 'Variables:' + '\033[0m\n'
        out += ', '.join(str(var) for var in self.vars)
        out += '\n\033[4m' + 'Assumptions:' + '\033[0m\n'
        out += '\n'.join(str(assumption) for assumption in self.assumptions) if self.assumptions else 'None'
        out += '\n\033[4m' + 'Goal:' + '\033[0m\n'
        out += str(self.goal)
        return out

class Solution:
    """Solution for a problem"""

    def __init__(self, problem: Problem):
        assert isinstance(problem, Problem), "Solution.__init__() takes Problem"
        self.vars = problem.vars
        self.goals = [problem.goal]
        self.facts = list(problem.assumptions)
        self.terms = list(self.vars)
        for lhs, rhs in [(prop.lhs, prop.rhs) for prop in self.facts + self.goals]:
            if lhs.hasvar() and (lhs not in self.terms):
                self.terms.append(lhs)
            if rhs.hasvar() and (rhs not in self.terms):
                self.terms.append(rhs)
        self.history = [
            f"we will prove for all {', '.join(str(var) for var in self.vars)}:",
            str(self.goals[0]),
            *(f"assuming: {str(fact)}" for fact in self.facts),
            "here we go!"
        ]
    
    def __str__(self):
        out = '\033[4m' + 'Variables:' + '\033[0m\n'
        out += ', '.join(str(var) for var in self.vars)
        out += '\n\033[4m' + 'Terms under consideration:' + '\033[0m\n'
        out += '\n'.join(str(term) for term in self.terms)
        out += '\n\033[4m' + 'Facts assumed or derived:' + '\033[0m\n'
        out += '\n'.join(str(fact) for fact in self.facts) if self.facts else 'None'
        out += '\n\033[4m' + 'Main goal:' + '\033[0m\n'
        out += str(self.goals[0])
        out += '\n\033[4m' + 'Alternative goals:' + '\033[0m\n'
        out += '\n'.join(str(goal) for goal in self.goals[1:]) if self.goals[1:] else 'None'
        return out

    def print_history(self):
        for line in self.history:
            print(line)
    
    def add_history(self, message: str|list = ''):
        assert isinstance(message, (str, list, tuple)), "Solution.add_history() takes str or list"
        if message:
            if isinstance(message, str):
                self.history.append(message)
            else:
                for msg in message:
                    self.history.append(msg)

    def add_term(self, term: Term, message=''):
        assert isinstance(term, Term), "Solution.add_term() takes Term"
        if term.hasvar() and (term not in self.terms):
            self.terms.append(term)
            self.add_history(message)
            return True
        return False
    
    def add_fact(self, fact: Prop, message=''):
        assert isinstance(fact, Prop), "Solution.add_fact() takes Prop"
        if fact.hasvar() and (fact not in self.facts):
            self.facts.append(fact)
            self.add_term(fact.lhs)
            self.add_term(fact.rhs)
            self.add_history(message)
            return True
        return False

    def add_goal(self, goal: Le, message=''):
        assert isinstance(goal, Le), "Solution.add_goal() takes Le"
        if goal not in self.goals:
            self.goals.append(goal)
            self.add_term(goal.lhs)
            self.add_term(goal.rhs)
            self.add_history(message)
            return True
        return False

    def deduce(self):
        pass

from math_objects import *

class Deduce:
    """Class for deduction rules"""

    def __init__(self, statement, *assumptions):
        self.statement = statement
        self.assumptions = assumptions
    
    def __repr__(self):
        return f"Deduce({self.statement}" + (f", assuming: {', '.join(str(a) for a in self.assumptions)})" if self.assumptions else ")")

deduction_rules = {
    'square_is_positive': Deduce(Le(0, Unk('X')**2)),
    'add_ineqs': Deduce(Le(Unk('X1') + Unk('X2'), Unk('Y1') + Unk('Y2')), Le(Unk('X1'), Unk('Y1')), Le(Unk('X2'), Unk('Y2'))),
}

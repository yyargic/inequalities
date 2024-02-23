# Term: Const | Var | Unk | Op
# Prop: Eq | Le

class Term:
    """Terms, for example: 15, x, y^2+1"""

    def __init__(self):
        assert self.__class__ != Term, "The Term class should only be used through its children"
    
    def __add__(self, other):
        return Add(self, other)
    
    def __radd__(self, other):
        return Add(other, self)
    
    def __sub__(self, other):
        return Sub(self, other)
    
    def __rsub__(self, other):
        return Sub(other, self)
    
    def __mul__(self, other):
        return Mul(self, other)
    
    def __rmul__(self, other):
        return Mul(other, self)
    
    def __truediv__(self, other):
        return Div(self, other)
    
    def __rtruediv__(self, other):
        return Div(other, self)
    
    def __pow__(self, other):
        return Pow(self, other)
    
    def __rpow__(self, other):
        return Pow(other, self)
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        return Sub(0, self)
    
    def __iter__(self):
        yield self
        if isinstance(self, Op):
            for arg in self.args:
                yield from iter(arg)

    def isconst(self):
        return not any(isinstance(term, (Var, Unk)) for term in self)
    def hasvar(self):
        return any(isinstance(term, Var) for term in self)
    def hasunk(self):
        return any(isinstance(term, Unk) for term in self)

    def isinstance_add(self):
        return isinstance(self, Op) and self.ftype == 'Add'
    def isinstance_sub(self):
        return isinstance(self, Op) and self.ftype == 'Sub'
    def isinstance_mul(self):
        return isinstance(self, Op) and self.ftype == 'Mul'
    def isinstance_div(self):
        return isinstance(self, Op) and self.ftype == 'Div'
    def isinstance_pow(self):
        return isinstance(self, Op) and self.ftype == 'Pow'
    def isinstance_root(self):
        return isinstance(self, Op) and self.ftype == 'Root'
    
    def isneg_const(self):
        return isinstance(self, Const) and self.value < 0
    def isneg_sub(self):
        return self.isinstance_sub() and self.args[0] == Const(0)

class Const(Term):
    """Constant real numbers"""

    def __init__(self, value):
        if isinstance(value, complex): raise ArithmeticError("Complex number encountered")
        assert isinstance(value, (int, float)), "Const.__init__() takes int or float"
        super().__init__()
        self.value = value
    
    def __repr__(self):
        return f"Const({self.value})"

    def __str__(self):
        if self.value == int(self.value):
            return f"{int(self.value)}"
        else:
            return f"{self.value:.4f}"
    
    def __eq__(self, other):
        return isinstance(other, Const) and self.value == other.value
    
    def __lt__(self, other):
        if not isinstance(other, Const):
            raise TypeError(f"'<' not supported between instances of 'Const' and '{other.__class__.__name__}'")
        return self.value < other.value

class Var(Term):
    """Real variables"""
    
    def __init__(self, name):
        assert isinstance(name, str), "Var.__init__() takes str"
        assert name, "The variable name must be a non-empty string"
        assert name.isalnum(), "The variable name must be alpha-numeric"
        assert name[0].isalpha(), "The first character of the variable name must be alphabetic"
        super().__init__()
        self.name = name
    
    def __repr__(self):
        return f"Var('{self.name}')"

    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name
    
    def __lt__(self, other):
        if not isinstance(other, Var):
            raise TypeError(f"'<' not supported between instances of 'Var' and '{other.__class__.__name__}'")
        return self.name < other.name

class Unk(Term):
    """Unknown place holders for all terms"""
    
    def __init__(self, name):
        assert isinstance(name, str), "Unk.__init__() takes str"
        super().__init__()
        self.name = name
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"
    
    def __str__(self):
        return self.name
    
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

class Unk_Const(Unk):
    """Unknown place holders for constants"""
    def __init__(self, name):
        super().__init__(name)

class Op(Term):
    """Operations between terms"""

    def __init__(self, ftype, *args):
        ftype_options = {'Add': 0, 'Sub': 2, 'Mul': 0, 'Div': 2, 'Pow': 2, 'Root': 2}
        assert ftype in ftype_options, f"The operation type must be one of the following: {tuple(ftype_options.keys())}"
        assert all(isinstance(arg, Term) for arg in args), f"Op.__init__({ftype}, *args) takes Term arguments"
        if ftype_options[ftype] == 2:
            assert len(args) == 2, f"Op.__init__({ftype}, *args) takes 2 positional argument but {len(args)} were given"
        super().__init__()
        self.ftype = ftype
        self.ftype_group = ftype_options[ftype]
        self.args = args
    
    def __repr__(self):
        return f"{self.ftype}({', '.join(repr(arg) for arg in self.args)})"
    
    def __str__(self):
        match self.ftype:
            case 'Add':
                lesser_ops = ('Add', 'Sub')
                if not self.args:
                    return "0_empty"
                else:
                    return "+".join(f"({arg})" if isinstance(arg, Op) and arg.ftype in lesser_ops else f"{arg}" for arg in self.args)
            case 'Sub':
                lesser_ops = ('Add', 'Sub')
                if self.args[0] == Const(0):
                    return f"-({self.args[1]})" if isinstance(self.args[1], Op) and self.args[1].ftype in lesser_ops else f"-{self.args[1]}"
                else:
                    return "-".join(f"({arg})" if isinstance(arg, Op) and arg.ftype in lesser_ops else f"{arg}" for arg in self.args)
            case 'Mul':
                lesser_ops = ('Add', 'Sub', 'Mul', 'Div')
                if not self.args:
                    return "1_empty"
                else:
                    return "*".join(f"({arg})" if isinstance(arg, Op) and arg.ftype in lesser_ops else f"{arg}" for arg in self.args)
            case 'Div':
                lesser_ops = ('Add', 'Sub', 'Mul', 'Div')
                return "/".join(f"({arg})" if isinstance(arg, Op) and arg.ftype in lesser_ops else f"{arg}" for arg in self.args)
            case 'Pow':
                lesser_ops = ('Add', 'Sub', 'Mul', 'Div', 'Pow', 'Root')
                return "^".join(f"({arg})" if isinstance(arg, Op) and arg.ftype in lesser_ops else f"{arg}" for arg in self.args)
            case 'Root':
                return str(Op('Pow', self.args[0], Op('Div', Const(1), self.args[1])))

    def __eq__(self, other):
        if not isinstance(other, Op):
            return False
        if self.ftype != other.ftype:
            return False
        if self.ftype_group == 0:
            return all(self.args.count(arg) == other.args.count(arg) for arg in self.args + other.args)
        else:
            return self.args == other.args

def _wrap(x):
    """This allows easy typing of constants and variables"""
    if isinstance(x, (int, float)):
        return Const(x)
    if isinstance(x, str):
        return Var(x)
    if isinstance(x, tuple):
        return tuple(_wrap(i) for i in x)
    return x

def Add(*args):
    return Op('Add', *_wrap(args))
def Sub(*args):
    return Op('Sub', *_wrap(args))
def Mul(*args):
    return Op('Mul', *_wrap(args))
def Div(*args):
    return Op('Div', *_wrap(args))
def Pow(*args):
    return Op('Pow', *_wrap(args))
def Root(*args):
    return Op('Root', *_wrap(args))

class Prop:
    """Propositions, for example: x-y=1, 2*x*y<=x^2+y^2"""

    def __init__(self, lhs, rhs):
        self.lhs, self.rhs = _wrap(lhs), _wrap(rhs)
        assert self.__class__ != Prop, "The Prop class should only be used through its children"
        assert isinstance(self.lhs, Term) and isinstance(self.rhs, Term), "Prop.__init__() takes Term"
    
    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.lhs)}; {repr(self.rhs)})"
    
    def __str__(self):
        relation = {'Eq': '=', 'Le': '<='}[self.__class__.__name__]
        return str(self.lhs) + relation + str(self.rhs)
    
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if isinstance(self, Eq):
            return (self.lhs, self.rhs) == (other.lhs, other.rhs) or (self.lhs, self.rhs) == (other.rhs, other.lhs)
        if isinstance(self, Le):
            return (self.lhs, self.rhs) == (other.lhs, other.rhs)

    def __iter__(self):
        yield from iter(self.lhs)
        yield from iter(self.rhs)
    
    # def isrefl(self):
    #     return self.lhs == self.rhs
    # def isconst(self):
    #     return not any(isinstance(term, (Var, Unk)) for term in self)
    def hasvar(self):
        return any(isinstance(term, Var) for term in self)
    def hasunk(self):
        return any(isinstance(term, Unk) for term in self)

class Eq(Prop):
    """Equality (=) propositions"""
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)
    
    def rev(self):
        return Eq(self.rhs, self.lhs)

class Le(Prop):
    """Inquality (<=) propositions"""
    def __init__(self, lhs, rhs):
        super().__init__(lhs, rhs)

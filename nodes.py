# Term: Const | Var | Unk | Op

class Term:
    """Terms are constants, variables, or the non-evaluating operations between them, e.g., x+1"""
    
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

class Const(Term):
    """Constant real numbers"""

    def __init__(self, value):
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

def wrap(x):
    """This allows easy typing of constants and variables"""
    if isinstance(x, (int, float)):
        return Const(x)
    if isinstance(x, str):
        return Var(x)
    if isinstance(x, tuple):
        return tuple(wrap(i) for i in x)
    return x

def Add(*args):
    return Op('Add', *wrap(args))
def Sub(*args):
    return Op('Sub', *wrap(args))
def Mul(*args):
    return Op('Mul', *wrap(args))
def Div(*args):
    return Op('Div', *wrap(args))
def Pow(*args):
    return Op('Pow', *wrap(args))
def Root(*args):
    return Op('Root', *wrap(args))

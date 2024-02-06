from dataclasses import dataclass
from itertools import combinations
from types import FunctionType

# Any : Prop | Term_ | Term
# Prop and Term_ wrap Term instances
# Prop : Eq | Le
# Term : Const | Var | Op
# Op : Add | Sub | Neg | Mul | Div | Inv | Pow | Root | Cyc3

@dataclass
class Term:
    """Terms are mathematical expressions that cannot be true or false, e.g., 1+2"""
    
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
        if isinstance(self, Neg):
            return self.x
        else:
            return Neg(self)
    
    def __iter__(self):
        yield self
    
    def __lt__(self, other):
        if {self.__class__.__name__, other.__class__.__name__} == {Add, Cyc3}:
            return None
        if self.__class__.__name__ < other.__class__.__name__:
            return True
        if self.__class__.__name__ > other.__class__.__name__:
            return False
    
    def isconst(self):
        return not any(isinstance(child, Var) for child in self)

@dataclass
class Const(Term):
    """Constant real number"""
    value: int | float

    def __init__(self, value):
        assert isinstance(value, (int, float)), "The input to Const must be int or float"
        super().__init__()
        self.value = value
        self.op_tree = ['Const', self.value]
    
    def __repr__(self):
        return f"Const({self.value})"

    def __str__(self):
        if self.value == int(self.value):
            return f"{int(self.value)}"
        else:
            return f"{self.value:.4f}"
    
    def __lt__(self, other):
        sup = super().__lt__(other)
        return sup if sup is not None else self.value < other.value

@dataclass
class Var(Term):
    """Real variable"""
    name: str

    def __init__(self, name):
        assert isinstance(name, str), "The input to Var must be str"
        assert name, "The variable name must be a non-empty string"
        assert name.isalnum(), "The variable name must be alpha-numeric"
        assert name[0].isalpha(), "The first character of the variable name must be alphabetic"
        super().__init__()
        self.name = name
        self.op_tree = ['Var', self.name]
    
    def __repr__(self):
        return f"Var('{self.name}')"

    def __str__(self):
        return self.name
    
    def __lt__(self, other):
        sup = super().__lt__(other)
        return sup if sup is not None else self.name < other.name

@dataclass
class Op(Term):
    """A term built through a mathematical operation on smaller terms"""
    args: tuple[Term]

    def __init__(self, *args):
        super().__init__()
        if not isinstance(self, Cyc3):
            self.args = wrap(args)
            self.op_tree = [self.__class__.__name__, *(arg.op_tree for arg in self.args)]
    
    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(repr(arg) for arg in self.args)})"
    
    def __eq__(self, other):
        if isinstance(self, (Add, Cyc3)):
            if not isinstance(other, (Add, Cyc3)):
                return False
            else:
                return sorted(self.args) == sorted(other.args)
        elif self.__class__ != other.__class__:
            return False
        elif isinstance(self, Mul):
            return sorted(self.args) == sorted(other.args)
        else:
            return self.args == other.args

    def __lt__(self, other):
        sup = super().__lt__(other)
        if sup is not None:
            return sup
        elif isinstance(self, (Add, Mul, Cyc3)):
            return sorted(self.args) < sorted(other.args)
        else:
            return self.args < other.args
    
    def __iter__(self):
        yield self
        if isinstance(self, Add):
            for length in range(2, len(self.args)):
                for subset in combinations(self.args, length):
                    yield Add(*subset)
        if isinstance(self, Mul):
            for length in range(2, len(self.args)):
                for subset in combinations(self.args, length):
                    yield Mul(*subset)
        if isinstance(self, Cyc3):
            for subset in combinations(self.args, 2):
                yield Add(*subset)
        for arg in self.args:
            yield from iter(arg)

@dataclass(repr=False, eq=False)
class Add(Op):
    """Sum of aribtrarily many terms"""
    args: tuple[Term]

    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        lesser_ops = (Add, Sub)
        return "+".join(f"({arg})" if isinstance(arg, lesser_ops) else f"{arg}" for arg in self.args)

@dataclass(repr=False, eq=False)
class Sub(Op):
    """Difference of two terms"""
    args: tuple[Term]

    def __init__(self, *args):
        assert len(args) == 2, f"Sub.__init__() takes 2 positional arguments but {len(args)} were given"
        super().__init__(*args)

    def __str__(self):
        lesser_ops = (Add, Sub)
        return "-".join(f"({arg})" if isinstance(arg, lesser_ops) else f"{arg}" for arg in self.args)

@dataclass(repr=False, eq=False)
class Neg(Op):
    """-x"""
    args: tuple[Term]

    def __init__(self, *args):
        assert len(args) == 1, f"Neg.__init__() takes 1 positional argument but {len(args)} were given"
        super().__init__(*args)

    def __str__(self):
        x, = self.args
        lesser_ops = (Add, Sub)
        return f"-({x})" if isinstance(x, lesser_ops) else f"-{x}"

@dataclass(repr=False, eq=False)
class Mul(Op):
    """Product of aribtrarily many terms"""
    args: tuple[Term]

    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        lesser_ops = (Add, Sub, Neg, Mul, Div, Inv)
        return "*".join(f"({arg})" if isinstance(arg, lesser_ops) else f"{arg}" for arg in self.args)

@dataclass(repr=False, eq=False)
class Div(Op):
    """Ratio of two terms"""
    args: tuple[Term]

    def __init__(self, *args):
        assert len(args) == 2, f"Div.__init__() takes 2 positional arguments but {len(args)} were given"
        super().__init__(*args)

    def __str__(self):
        lesser_ops = (Add, Sub, Neg, Mul, Div, Inv)
        return "/".join(f"({arg})" if isinstance(arg, lesser_ops) else f"{arg}" for arg in self.args)

@dataclass(repr=False, eq=False)
class Inv(Op):
    """1/x"""
    args: tuple[Term]

    def __init__(self, *args):
        assert len(args) == 1, f"Inv.__init__() takes 1 positional argument but {len(args)} were given"
        super().__init__(*args)

    def __str__(self):
        x, = self.args
        lesser_ops = (Add, Sub, Neg, Mul, Div, Inv)
        return f"1/({x})" if isinstance(x, lesser_ops) else f"1/{x}"

@dataclass(repr=False, eq=False)
class Pow(Op):
    """arg1 ^ arg2"""
    args: tuple[Term]

    def __init__(self, *args):
        assert len(args) == 2, f"Pow.__init__() takes 2 positional arguments but {len(args)} were given"
        super().__init__(*args)

    def __str__(self):
        lesser_ops = (Add, Sub, Neg, Mul, Div, Inv, Pow, Root)
        return "^".join(f"({arg})" if isinstance(arg, lesser_ops) else f"{arg}" for arg in self.args)

@dataclass(repr=False, eq=False)
class Root(Op):
    """arg1 ^ (1/arg2)"""
    args: tuple[Term]

    def __init__(self, *args):
        assert len(args) == 2, f"Root.__init__() takes 2 positional arguments but {len(args)} were given"
        super().__init__(*args)

    def __str__(self):
        l, r = self.args
        lesser_ops = (Add, Sub, Neg, Mul, Div, Inv, Pow, Root)
        str_l = f"({l})" if isinstance(l, lesser_ops) else f"{l}"
        match r:
            case Const(2):
                return f"\u221a{str_l}"
            case Const(3):
                return f"\u221b{str_l}"
            case Const(4):
                return f"\u221c{str_l}"
            case _:
                lesser_ops = (Add, Sub, Neg, Mul, Div, Inv)
                str_r = f"({r})" if isinstance(r, lesser_ops) else f"{r}"
                return f"{str_l}^(1/{str_r})"

@dataclass(eq=False)
class Cyc3(Op):
    """f(a,b,c)+f(b,c,a)+f(c,a,b)"""
    f: FunctionType
    a: Var
    b: Var
    c: Var

    def __init__(self, f, a, b, c, *bases):
        assert isinstance(f, FunctionType), "f in Cyc3.__init__(f, a, b, c) must be FunctionType"
        assert isinstance(a, Var) and isinstance(b, Var) and isinstance(c, Var), "a,b,c in Cyc3.__init__(f, a, b, c) must be Var"
        assert all(isinstance(base, Cyc3) for base in bases), "The bases in Cyc3.__init__(f, a, b, c, *bases) must be Cyc3"
        super().__init__()
        self.f, self.a, self.b, self.c = f, wrap(a), wrap(b), wrap(c)
        self.bases = bases # This is a tuple of other Cyc3 instances to build upon
        self.f3 = self.f if not self.bases else lambda a, b, c: self.f(a, b, c, *(base.f3(a, b, c) for base in self.bases))
        self.out = self.f3(self.a, self.b, self.c)
        self.args = (self.out, self.f3(self.b, self.c, self.a), self.f3(self.c, self.a, self.b))
        self.op_tree = ['Cyc3', self.out.op_tree]

    def __repr__(self):
        out_repr = repr(self.f3(Var('a'), Var('b'), Var('c')))
        for long, short in (("Var('a')", "a"), ("Var('b')", "b"), ("Var('c')", "c")):
            while long in out_repr:
                idx = out_repr.index(long)
                out_repr = out_repr[:idx] + short + out_repr[idx+len(long):]
        return f"Cyc3(lambda a, b, c: {out_repr}, {repr(self.a)}, {repr(self.b)}, {repr(self.c)})"

    def __str__(self):
        return f"({self.out}+cyc.)"

@dataclass
class Term_:
    """Wrapper for Term, because I need to change Term instances"""
    term: Term

    def __str__(self):
        return str(self.term)

@dataclass
class Prop:
    """Propositions are mathematical statements that can be true or false, e.g., 1+2=3"""
    
    def __iter__(self):
        yield from iter(self.lhs)
        yield from iter(self.rhs)

@dataclass
class Eq(Prop):
    """Equality of two terms"""
    lhs: Term
    rhs: Term

    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs, self.rhs = wrap(lhs), wrap(rhs)

    def __str__(self):
        return f"{self.lhs}={self.rhs}"

@dataclass
class Le(Prop):
    """Less-than-or-equal ordering of two terms"""
    lhs: Term
    rhs: Term

    def __init__(self, lhs, rhs):
        super().__init__()
        self.lhs, self.rhs = wrap(lhs), wrap(rhs)

    def __str__(self):
        return f"{self.lhs}<={self.rhs}"

def wrap(x):
    """This allows easy typing of constants and variables."""
    assert isinstance(x, (Term, int, float, str, tuple)), "The input to wrap must be a Term, int, float, str, or tuple."
    if isinstance(x, Term):
        return x
    if isinstance(x, (int, float)):
        return Const(x)
    if isinstance(x, str):
        return Var(x)
    if isinstance(x, tuple):
        return tuple(wrap(i) for i in x)

def parse(string):
    """This allows fast typing of terms and propositions, especially for testing."""
    if not isinstance(string, str): raise TypeError("The input must be a string.")
    string = ''.join(ch for ch in string if ch != ' ')
    if string == '': raise SyntaxError("Empty string encountered.")
    if not string.count('(') == string.count(')'): raise SyntaxError("Parentheses do not match")
    if not all(string[:i+1].count('(') >= string[:i+1].count(')') for i, _ in enumerate(string)): raise SyntaxError("Parentheses do not match")
    match string.count('='):
        case 0:
            unmasked = [string[:i+1].count('(') <= string[:i+1].count(')') for i, _ in enumerate(string)]
            overview = [ch for ch, unm in zip(string, unmasked) if unm]
            unm_count = lambda s, ch, unm: [c for c, u in zip(s, unm) if u].count(ch)
            unm_index = lambda s, ch, unm: [c if u else (',' if ch != ',' else ';') for c, u in zip(s, unm)].index(ch)
            unm_split = lambda s, ch, unm: (lambda s, ch, unm, idx: [s[:idx]] + unm_split(s[idx+1:], ch, unm[idx+1:]))(s, ch, unm, unm_index(s, ch, unm)) if unm_count(s, ch, unm) else [s]
            if '+' in overview:
                unm_splitted = unm_split(string, '+', unmasked)
                if unm_splitted[0] == '' and len(unm_splitted) == 2:
                    return parse(unm_splitted[1])
                if unm_splitted[0] == '' and len(unm_splitted) > 2:
                    return Add(*(parse(block) for block in unm_splitted[1:]))
                else:
                    return Add(*(parse(block) for block in unm_splitted))
            if '-' in overview:
                unm_splitted = unm_split(string, '-', unmasked)
                if unm_splitted[0] == '' and len(unm_splitted) == 2:
                    return Neg(parse(unm_splitted[-1]))
                else:
                    return Sub(parse('-'.join(unm_splitted[:-1])), parse(unm_splitted[-1]))
            if '*' in overview:
                return Mul(*(parse(block) for block in unm_split(string, '*', unmasked)))
            if '/' in overview:
                unm_splitted = unm_split(string, '/', unmasked)
                return Div(parse('/'.join(unm_splitted[:-1])), parse(unm_splitted[-1]))
            if '^' in overview:
                unm_splitted = unm_split(string, '^', unmasked)
                return Pow(parse(unm_splitted[0]), parse('^'.join(unm_splitted[1:])))
            if string[0] == '\u221a':
                return Root(parse(string[1:]), 2)
            if string[0] == '\u221b':
                return Root(parse(string[1:]), 3)
            if string[0] == '\u221c':
                return Root(parse(string[1:]), 4)
            if string[0] == '(' and string[-1] == ')':
                return parse(string[1:-1])
            if string.isalnum() and string[0].isalpha():
                return Var(string)
            if string.isnumeric():
                return Const(int(string))
            if string.count('.') == 1:
                l, r = string.split('.')
                if string != '.' and (l.isnumeric() or not l) and (r.isnumeric() or not r):
                    return Const(float(string))
            raise SyntaxError
        case 1:
            if '<=' in string:
                l, r = string.split('<=')
                return Le(parse(l), parse(r))
            elif '>=' in string:
                l, r = string.split('>=')
                return Le(parse(r), parse(l))
            else:
                l, r = string.split('=')
                return Eq(parse(l), parse(r))
        case _:
            raise Exception("Writing multiple relations is not supported.")

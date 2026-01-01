import copy

class Base(object):
    def __init__(self):
        self.base_init = True

    def foo(self):
        return 'base foo'

    def bar(self):
        return 'base bar'

class Child(Base):
    def __new__(cls, other):
        if isinstance(other, Base):
            other = copy.copy(other)
            other.__class__ = Child
            return other
        return object.__new__(cls)

    def __init__(self, other):
        self.child_init = True

    def bar(self):
        return 'child bar'
    
b = Base()
assert b.base_init == True
assert b.foo() == 'base foo'
assert b.bar() == 'base bar'
assert b.__class__ == Base

c = Child(b)
assert c.base_init == True
assert c.child_init == True
assert c.foo() == 'base foo'
assert c.bar() == 'child bar'
assert c.__class__ == Child
assert b.__class__ == Base
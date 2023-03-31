from yaclipy_tools.singleton import Singleton

class ClsA(metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

class ClsB(ClsA): pass

class ClsC(metaclass=Singleton):
    @classmethod
    def init_once(self, *args, **kwargs):
        print(f"init_once {args} {kwargs}")
        self.args = args
    
    def __init__(self, **kwargs):
        print(f"__init__ {kwargs}")
        self.kwargs = kwargs



def test_singleton_clsa():
    c1 = ClsA(1,2,3,c=5,d=6)
    assert(c1.kwargs.keys() == {'c','d'})
    c2 = ClsA(1,2,3,c=0)
    assert(id(c1) != id(c2))
    assert(id(c1.__class__) == id(c2.__class__))
    b1 = ClsB(1,2,3,c=5,d=6)
    assert(id(b1.__class__) != id(c1.__class__))
    

def test_singleton_2():
    c1 = ClsC(1,2,3, c=4, d=5)
    assert(c1.args == (1,2,3))
    assert(c1.kwargs == {'c':4,'d':5})
    c2 = ClsC(1,2,3, c=4, d=5)
    assert(id(c1.args) == id(c2.args))
    assert(c2.kwargs == {'c':4,'d':5})
    assert(id(c2.kwargs) != id(c1.kwargs))
    


def test_singleton_kwargs():
    class A(metaclass=Singleton):
        @classmethod
        def init_once(self, *args, **kwargs):
            assert(kwargs == {'a':3})
        def __init__(self, *args, **kwargs):
            pass

    A(3,3,a=3)

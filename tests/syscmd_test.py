import pytest
from print_ext import print
from yaclipy_tools import SysTool
from yaclipy_tools.sys_tool import MissingTool
from .testutil import printer


class MyTool(SysTool):
    @classmethod
    def init_once(self, *args):
        print(f"MY TOOL init_once {args}")
        super().init_once(*args)

    @classmethod
    def version(self):
        return '1.4.3'
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class OtherTool(SysTool):
    @classmethod
    def version(self):
        return '3.5'

    def __init__(self, **kwargs):
        self.kwargs = kwargs



def test_systool_exception():
    MyTool('1')
    with pytest.raises(MissingTool):
        MyTool('2')
    with pytest.raises(MissingTool):
        MyTool('1.4.4')

    try:
        MyTool('1.5.0')
    except MissingTool as e:
        o,p = printer()
        p.pretty(e)
        assert('1.5.0' in o.getvalue())
        

if __name__ == '__main__':
    m1 = MyTool('1', verbose=2)
    assert(m1.kwargs['verbose'] == 3)
    #m2 = MyTool('2', verbose=2)
    #m3 = MyTool('1', verbose=3)
    #o2 = OtherTool('2', verbose=2)
    #print(id(m1), id(m2), id(m3), id(o2))


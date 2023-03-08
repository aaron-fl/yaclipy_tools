import pytest
from print_ext import print
from yaclipy_tools import SysTool
from yaclipy_tools.sys_tool import MissingTool
from .testutil import printer


class MyTool(SysTool):
    def version(self):
        return '1.4.3'

class OtherTool(SysTool):
    def version(self):
        return '3.5'

def test_systool_singleton():
    t = OtherTool("1")
    t2 = MyTool("1")
    t3 = MyTool("1")
    t4 = MyTool("1.2")
    assert(t != t2)
    assert(t2 == t3)
    assert(t2 != t4)
    assert(len(MyTool._instances) == 2)


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
        
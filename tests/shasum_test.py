from print_ext import print
from yaclipy_tools.shasum import Shasum
from yaclipy_tools.sys_tool import MissingTool

def test_Shasum():
    try:
        sha = Shasum('11')
        assert(False)
    except MissingTool as e: 
        print.pretty(e)
    sha = Shasum('6')
    assert(sha.hash('tests/echo.py') == '0330b869605febca1969554eeb9002c84a1148c7')

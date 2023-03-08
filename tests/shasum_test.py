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
    assert(sha.hash('tests/echo.py') == '00ee7a5c16749b16a0e158774a77f87e9bc4e9d8')

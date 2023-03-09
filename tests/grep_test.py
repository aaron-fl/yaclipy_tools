from print_ext import print
from yaclipy_tools.sys_tool import MissingTool
from yaclipy_tools.grep import Grep, grep, grep_groups



def test_grep_source():
    grep_groups(dict(gg=[(None, 'tests/grep_test.py', 'tests/echo.py')]))
    results = grep('none') # More NONEnone
    print.pretty(results)
    assert(len(results['gg']) == 2)
    assert(results['gg'][0].fname == 'tests/grep_test.py')
    

if __name__ == '__main__':
    test_grep_source()

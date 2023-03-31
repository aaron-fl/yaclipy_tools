import pytest
from print_ext import Printer
from yaclipy_tools.all import Grep
from yaclipy_tools.commands import grep, grep_groups
from .testutil import get_tool


@pytest.mark.asyncio
async def test_grep_source():
    g = await get_tool(Grep())
    grep_groups(dict(gg=[(None, 'tests/grep_test.py', 'tests/echo.py')]))
    results = await grep('none') # More NONEnone
    Printer().pretty(results)
    assert(len(results['gg']) == 2)
    assert(results['gg'][0].fname == 'tests/grep_test.py')
    

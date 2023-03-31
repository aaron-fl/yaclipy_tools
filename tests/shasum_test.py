import pytest
from yaclipy_tools.all import Shasum
from .testutil import get_tool


@pytest.mark.asyncio
async def test_Shasum():    
    sha = await get_tool(Shasum('6'))
    assert(await sha.hash('tests/echo.py') == 'a2dce0d96742f159a875e4fc24c3966e7f836425')

import pytest
from yaclipy_tools.all import Md5
from .testutil import get_tool

@pytest.mark.asyncio
async def test_md5():
    md5 = await get_tool(Md5())
    assert(await md5.hash('tests/echo.py') == 'd0130dc0b9073e42b5211ad2c10130d9')

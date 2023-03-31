import pytest
from print_ext import Printer
from yaclipy_tools.all import GPG
from .testutil import get_tool


@pytest.mark.asyncio
async def test_gpg():
    gpg = await get_tool(GPG('2.3'))
    assert(await gpg.import_key('x') == None)

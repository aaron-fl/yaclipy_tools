import pytest
from print_ext import Printer
from yaclipy_tools.all import Nginx
from .testutil import get_tool


@pytest.mark.asyncio
async def test_nginx_config():
    nginx = await get_tool(Nginx('1.20'))
    Printer().pretty(nginx.cfg_tree)
    assert('pid local/nginx/nginx.pid' in nginx.cfg_tree)



@pytest.mark.asyncio
async def test_nginx_run():
    nginx = await get_tool(Nginx('1.20'))
    await nginx.start()
    print("RUNNING")
    await nginx.stop()

import pytest, asyncio, pathlib
from print_ext import Printer
from yaclipy_tools.all import Git
from .testutil import get_tool

@pytest.mark.asyncio
async def test_git_name():
    git = await get_tool(Git('2.30'))
    assert(await git.name == 'yaclipy_tools')
    assert(len(await git.current_commit()) == 40)
    assert(await git.current_branch() == 'main')


@pytest.mark.xfail()
@pytest.mark.asyncio
async def test_git_status():
    git = await get_tool(Git())
    Printer().pretty(await git.status())


@pytest.mark.asyncio
async def test_git_list():
    git = await get_tool(Git())
    l = [f async for f in git.list('*.py', invert=False)]
    assert(pathlib.Path('tests/echo.py') in l)
    Printer().pretty(l)

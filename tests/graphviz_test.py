import pytest
from print_ext import Printer
from yaclipy_tools.all import GraphViz
from yaclipy_tools import Log, Input
from yaclipy_tools.mio import MioFile
from .testutil import get_tool


@pytest.mark.asyncio
async def test_graphviz_plugins(tmp_path):
    dot = await get_tool(GraphViz(7))
    path = tmp_path/'f.dot'
    f = MioFile(path)
    print(f.path)
    lines = await dot('dot', '-P').log(f, 1)
    await f.close()
    await dot.gen('dot', path)


@pytest.mark.asyncio
async def test_graphviz_input(tmp_path):
    t = 'digraph {\na -> b;\n}'
    dot = await get_tool(GraphViz(7))
    await dot.gen('dot', '-', path=tmp_path/'test.png').input(t)

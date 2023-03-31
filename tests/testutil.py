import io, pytest, asyncio
from print_ext import Printer, StringIO, PrettyException
from yaclipy_tools.sys_tool import MissingTool


def tostr(*args, **kwargs):
    return str(Printer.using(StringIO)(**kwargs)(*args, **kwargs))



async def get_tool(tool):
    try:
        await tool.ensure()
        print(f"{tool.__class__.__name__} version: {await tool.version}")
    except PrettyException as e:
        Printer().pretty(e)
        #pytest.skip(str(e))
    return tool

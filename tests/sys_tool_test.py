import pytest, asyncio
from print_ext import Printer, StringIO
from yaclipy_tools import SysTool, ProcTask, Echo
from yaclipy_tools.sys_tool import MissingTool


class MyTool(SysTool):
    used_for = lambda: f"reasons"
    cmd = lambda: ''

    @classmethod
    def init_once(self, *args):       
        super().init_once(*args)
        print(f"MY TOOL init_once {args} {self.version.done()}")

    @classmethod
    async def get_version(self):
        await asyncio.sleep(0.1)
        return '1.4.3'
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self):
        return asyncio.create_task(self.show_version())
    
    async def show_version(self):
        await asyncio.sleep(0.1)
        return await self.version



class OtherTool(SysTool):
    @classmethod
    async def get_version(self):
        await asyncio.sleep(0.2)
        return '3.5'

    def __init__(self, **kwargs):
        self.kwargs = kwargs



@pytest.mark.asyncio
async def test_systool_version_check():
    m1 = MyTool('1')
    m2 = MyTool('2')
    m144 = MyTool('1.4.4')

    assert(await m1() == (1,4,3))
    with pytest.raises(MissingTool):
        await m2()
    with pytest.raises(MissingTool):
        await m144()



@pytest.mark.asyncio
async def test_systool_exception():
    m150 = MyTool('1.5.0')
    try:
        await m150()
    except MissingTool as e:
        p = Printer.using(StringIO)().pretty(e)
        print(p)
        assert('1.5.0' in str(p))
        assert('1.4.3' in str(p))
        assert('reasons' in str(p))



@pytest.mark.asyncio
async def test_systool_cmdnotfound():
    class _Tool(MyTool):
        @classmethod
        async def get_version(self):
            await ProcTask('not-a-real-command', 'version', '-v')

    with pytest.raises(MissingTool):
        await _Tool()()



@pytest.mark.asyncio
async def test_systool_get_version_raises():

    class _Tool(MyTool):
        @classmethod
        async def get_version(self):
            raise AttributeError("Done")

    tool = _Tool()
    with pytest.raises(AttributeError):
        await tool()
        

@pytest.mark.asyncio
async def test_systool_deps_exception():
    async def dep():
        raise NotImplementedError()

    class Tool(SysTool):
        cmd = lambda: 'ls'
        @classmethod
        def init_once(self, *args, **kwargs):
            task = asyncio.create_task(dep())
            print(f"Task {task}")
            super().init_once(*args, deps=[task], **kwargs)
        @classmethod
        async def get_version(self):
            return '1.0'
    
    tool = Tool('1')
    with pytest.raises(NotImplementedError):
        await tool().echo()

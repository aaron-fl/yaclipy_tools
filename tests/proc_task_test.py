import pytest, sys, pathlib, asyncio
from print_ext import Printer, Flatten
from print_ext.line import SMark as SM
from yaclipy_tools.proc_task import ProcTask, Log, Echo, Plugin, Lines, One, ReturncodeError

ECHO = ProcTask(sys.executable, '-m', 'tests.echo')


def test_proc_use():
    a = ECHO.use(Lines)
    assert(a.cmd[1:] == ('-m', 'tests.echo'))
    b = a(0)
    assert(b.cmd[1:] == ('-m', 'tests.echo', '0'))
    c =  b(1, 2)
    assert(c.cmd[1:] == ('-m', 'tests.echo', '0', '1', '2'))
    d = c.use(Lines)
    assert(d.cmd[1:] == ('-m', 'tests.echo', '0', '1', '2'))



@pytest.mark.asyncio
async def test_proc_task_echo():
    pt = ProcTask(sys.executable, '-m', 'tests.echo')
    pt2 = ECHO(3, success=[3])
    assert(await pt2 == 3)
    assert(pt2.result() == 3)
    with pytest.raises(AttributeError):
        pt.result()



@pytest.mark.asyncio
async def test_proc_task_log(tmp_path):
    #somefile = AIOFile('somefile.txt')
    
    with open(tmp_path/'test.txt', 'wb') as f:
        pv = ECHO.use(Log(f))(0, 'a', '!b')
        pv.start()
        print(pv.mio)
        await pv
        end = f.tell()
        assert(end == 4)
        await ECHO.use(Log(f,1))(0, 'c', '!d')
        with open(tmp_path/'test2.txt', 'wb') as f2:
            await ECHO.use(Log(f,2), Log(f2,1))(0, 'e', '!f')
    assert(open(tmp_path/'test.txt').read() == 'a\nb\nc\nf\n')
    assert(open(tmp_path/'test2.txt').read() == 'e\n')



@pytest.mark.skip(reason="low priority")
def test_proc_task_custom_mixins():
    class MyMixin(Plugin):
        @Plugin.export
        def m1(self):
            return str(self).upper()
        def m2(self):
            return 'y'

    class YourMixin(MyMixin):
        def m1(self):
            return str(self).lower() + super().my_method()
        Plugin.export
        def m2(self):
            return f"z{super().m2()}"

    pt = ProcTask().use(MyMixin, YourMixin)(name="Ab")
    assert(pt.m1() == 'AB')
    with pytest.raises(AttributeError):
        assert(pt.m2() == 'AB')



@pytest.mark.asyncio
async def test_proc_command_not_found():
    pt = ProcTask('not-a-command')
    with pytest.raises(FileNotFoundError):
        await pt



@pytest.mark.asyncio
async def test_proc_task_echo():
    p = Printer.using(Flatten)()
    echo = ProcTask().use(Echo(1,style='g'), Echo(2,style='r'), context=p.context())
    await echo(sys.executable, '-m', 'tests.echo', 0, 'e', '!f')
    for k in [r.styled() for r in p.flatten()]:
        assert(k in [('e', [SM('g',0,1)]), ('f', [SM('r',0,1)])])



@pytest.mark.asyncio
async def test_proc_task_lines_3():
    l0 = ECHO.use(Lines(3))(0, 'a')
    l1 =  l0('!b', 'c')
    assert(set(await l1) == set(['a','b','c']))
    l2 = await l0.use(Lines(2))('!d')
    assert(set(l2[0]) == set(['a','d']))
    assert(l2[1] == ['d'])



@pytest.mark.asyncio
async def test_proc_task_lines_only():
    echo = ECHO.use(Lines(2, only=2), Lines)
    a = await echo(0, 'a','b','!c', 'd', '!e', '!f')
    assert(a[0] == ['c','e'])
    assert(set(a[1]) == {'a','b','d'})



@pytest.mark.asyncio
async def test_proc_task_one_line():
    echo = ECHO.use(One(1), One(2, row=1))
    assert(await echo(0) == (None, None))
    assert(await echo(0)('a','b', '!c', 'd') == ('a', None))
    

@pytest.mark.asyncio
async def test_proc_task_return():
    diff = ProcTask('diff')

    assert( await diff('README.md', 'README.md') == 0)
    assert( await diff('README.md', 'pyproject.toml', success=True) == 1)
    assert( await diff('README.md', 'pyproject.toml', success=[0,1]) == 1)
    try:
        await diff('README.md', 'pyproject.toml')
    except ReturncodeError as e:
        Printer().pretty(e)
        return
    assert(0)


@pytest.mark.asyncio
async def test_proc_task_or_else():
    assert(await ECHO(0) == 0)
    assert(await ECHO(1, or_else='hi') == 'hi')

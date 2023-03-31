import pytest, asyncio, random, sys
from print_ext import Printer, StringIO
from yaclipy_tools.proc_task import ProcTask


async def main():
    Printer('before')
    async with Printer().task_group('hello', height_max=4) as grp:
        proc = ProcTask(sys.executable, '-m', 'tests.slow_echo', '0.5', fname='local/slow.txt', context=grp.context(), stdin='as.d.f.34.5.6.7.8.9.0.', echo=True)

        async def looker():
            with proc.stdout() as read:
                async for line in read.each_line():
                    Printer(f"Got a line")
        
        
        grp.pending.add(proc)
        grp.create_task(looker(), name="Look for stuff")
        #await asyncio.sleep(0.5)
        #raise AttributeError('bob')

    
    Printer('outside')



if __name__ == '__main__':
    asyncio.run(main())


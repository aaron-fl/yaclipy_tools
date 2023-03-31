import pytest, asyncio, pathlib, io
from yaclipy_tools.mio import MioFile, MioBuffer, TruncatedData


@pytest.mark.asyncio
async def test_mio_file_early_break(tmp_path):
    f = MioFile(str(tmp_path/'log.txt'))        
    async def reader():
        with f.reader() as read:
            async for line in read.each_line():
                return line.upper()
                break
    f.write('hello\nworld')
    assert(await asyncio.gather(reader(), f.close()) == ['HELLO', None])


@pytest.mark.asyncio
async def test_mio_file_lines(tmp_path):
    f = MioFile(str(tmp_path/'log.txt'))     
    expect = ['hello', 'world']   
    async def reader():
        with f.reader() as read:
            async for line in read.each_line():
                assert(line == expect.pop(0))
        return 'done'
    async def writer():
        await asyncio.sleep(0.1)
        f.write('hello\nworld')
        await f.close()
        return 'asdf'
    assert(await asyncio.gather(reader(), writer()) == ['done', 'asdf'])



@pytest.mark.asyncio
async def test_mio_file_write_only(tmp_path):
    f = MioFile(str(tmp_path/'log.txt'))
    f.write('hello\nworld')
    f.write(None)
    await f.close()



@pytest.mark.asyncio
async def test_mio_file_read_later(tmp_path):
    f = MioFile(str(tmp_path/'log.txt'))
    f.write('hello\nworld')
    
    async def reader():
        with f.reader() as read:
            l = 0
            async for line in read.each_line():
                l += 1
            assert(l == 2)
            async for line in read.each_line():
                l += 1
            assert(l == 4)
    async def writer():
        f.write(None)
        await asyncio.sleep(0.1)
        await f.close()
    await asyncio.gather(reader(), writer())



@pytest.mark.asyncio
async def test_mio_file_slow_reader(tmp_path):
    f = MioFile(str(tmp_path/'log.txt'))
    f.write('hello\nworld')
    async def reader():
        with f.reader() as read:
            await asyncio.sleep(0.2)
            l = 0
            async for line in read.each_line():
                l += 1
            assert(l == 2)
            async for line in read.each_line():
                l += 1
            assert(l == 4)
    async def writer():
        f.write(None)
        await asyncio.sleep(0.1)
        await f.close()
    await asyncio.gather(reader(), writer())



@pytest.mark.asyncio
async def test_mio_buffer_underrun_ok():
    b = MioBuffer(10)
    b.write('12345678\n0123')
    assert(b.overflowed == 0)
    b.write('456')
    assert(b.overflowed == 6)
    with pytest.raises(TruncatedData):
        b.reader()
    with b.reader(overflowed_ok=True) as read:
        itr = read.each_line().__aiter__()
        line = await itr.__anext__()
        assert(line == '78')
        b.write('012345')
        with pytest.raises(TruncatedData):
            await itr.__anext__()


@pytest.mark.xfail()
def test_file_creation_rotation():
    ''' Can we delete a file that is currently opened?.  How to keep just the last N files?
    '''
    raise(0)


def test_mio_compare(tmp_path):
    b10 = MioBuffer(10)
    b100 = MioBuffer(100)
    f = MioFile(str(tmp_path/'log.txt'))
    f2 = MioFile(str(tmp_path/'log2.txt'))
    assert(b10 < b100 and b100 > b10)
    assert(b10 < f and f > b10)
    assert(f < f2)
    assert(f > None and None < f)
    assert(None < b10 and b10 > None)
    assert(b10 > True and True < b10)
    assert(f > True and True < f)


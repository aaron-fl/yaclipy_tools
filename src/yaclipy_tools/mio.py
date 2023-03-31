import asyncio, io, os, weakref, pathlib
from print_ext import Printer


class FileClosed(Exception): pass

class TruncatedData(Exception): pass



class IterState():
    def __init__(self, parent, encoding, size, end):
        self.parent = parent
        self.eof = parent.eof
        self.end = end
        self.size = size
        self.encoding = encoding
        self.offset = 0
        self.partial = bytearray()
        self._notify = asyncio.Event()


    def __aiter__(self):
        return self


    async def __anext__(self):
        while True:
            if self.offset < 0: raise TruncatedData(f"Buffer Underrun: {self.offset}")
            # Get some data
            got = self._get_line()
            self.partial.extend(got)
            # If it has a new line then return it
            if self.partial and self.partial[-1] == 10:
                self.partial[-1:] = []
                return self.encoded_line()
            if got: continue # Maybe we can get some more data?
            if self.eof: # No new data will be coming.
                if self.partial: return self.encoded_line() # return the tail
                raise StopAsyncIteration()
            # Wait for new data
            await self._notify.wait()
            self._notify.clear()


    def encoded_line(self):
        out = self.partial.decode(self.encoding) if self.encoding else self.partial
        self.partial = bytearray()
        return out


    def notify(self, eof):
        if eof == None or eof == True:
            self.eof = eof
        else:
            self.offset -= eof
        self._notify.set()



class BufferIterState(IterState):
    def _get_line(self):
        try:
            e = self.parent.buffer.index(10, self.offset)
            d = self.parent.buffer[self.offset:e+1]
        except ValueError:
            d = self.parent.buffer[self.offset:]
        self.offset += len(d)
        return d



class StreamIterState(IterState):
    def _get_line(self):
        self.parent.stream.seek(self.offset)
        got = self.parent.stream.readline()
        if got: self.offset = self.parent.stream.tell()
        return got



class Reader():
    def __init__(self, parent):
        self.parent = parent
        self.iterators = set()


    def each_line(self, size=0, encoding='utf8', end='\n'):
        if self.done.done(): raise FileClosed(f"Can't iterate over a closed file.")
        itr = self.parent.LineIter(self.parent, encoding, size, end)
        self.iterators.add(itr)
        return itr


    def __enter__(self):
        self.done = asyncio.get_running_loop().create_future()
        self.parent.readers.add(self)
        return self


    def __exit__(self, *args):
        self.done.set_result(True)
        self.iterators.clear()
        self.parent.readers.remove(self)


    def __await__(self):
        yield from self.done.__iter__()


    def notify(self, eof):
        for itr in self.iterators:
            itr.notify(eof)



class MioBase():
    def __init__(self):
        self.eof = False
        self.readers = set()


    def write(self, data, encoding='utf8'):
        if data == None: # Signal EOF
            self.eof = True
            notify = True
        else:
            if self.eof: raise FileClosed(f"Can't write to closed file")
            notify = self._write(data if isinstance(data, bytes) else data.encode(encoding))
        for reader in self.readers:
            reader.notify(notify)

    
    def reader(self):
        return Reader(self)


    async def close(self):
        self.write(None)
        await asyncio.gather(*self.readers)


    def __aenter__(self):
        return self

    
    async def __aexit__(self, *args):
        await self.close()


    def __gt__(self, other):
        return not self.__lt__(other)


    def __lt__(self, other):
        if other == True: return False
        if other == None: return False
        raise TypeError(f"'<' not supported between instances of {self.__class__.__name__!r} and {other.__class__.__name__!r}")



class MioStream(MioBase):
    LineIter = StreamIterState

    def __init__(self, stream):
        super().__init__()
        self.stream = stream

    
    def _write(self, data):
        self.stream.seek(0, io.SEEK_END)
        self.stream.write(data)
        

    async def close(self):
        await super().close()
        self.stream.close()



class MioBuffer(MioBase):
    LineIter = BufferIterState

    def __init__(self, size=0):
        super().__init__()
        self.size = size or io.DEFAULT_BUFFER_SIZE
        self.overflowed = 0
        self.buffer = bytearray()


    def _write(self, data):
        self.buffer.extend(data)
        size = len(self.buffer)
        if size > 1.5*self.size:
            lost = size-self.size
            self.overflowed += lost
            self.buffer[:lost] = []
            return lost


    def reader(self, overflowed_ok=False):
        if self.overflowed and not overflowed_ok: raise TruncatedData(f"Missing start of data.  Pass overflowed_ok=True to continue anyway") 
        return super().reader()


    async def close(self):
        await super().close()
        self.buffer.clear()


    def __lt__(self, other):
        if isinstance(other, MioBuffer): return self.size < other.size
        if isinstance(other, MioFile): return True
        return super().__lt__(other)


class MioFile(MioStream):

    def __init__(self, path, tmp=False):
        self.tmp = tmp
        i = 0
        path = pathlib.Path(path)
        d,a,b = path.parent, path.stem, path.suffix
        while True:
            self.path = d/f"{a}_{i}{b}" if i else path
            i += 1
            try:
                stream = open(self.path, 'xb+', buffering=0)
            except FileExistsError:
                continue
            break
        super().__init__(stream)
        

    async def close(self):
        await super().close()
        if self.tmp: Printer(f"Remove: {self.path}", tag='v:2')
        if self.tmp: self.path.unlink()

    
    def __lt__(self, other):
        if isinstance(other, MioBuffer): return False
        if isinstance(other, MioFile): return True
        return super().__lt__(other)

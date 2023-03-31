import asyncio, io
from .plugin import Plugin


class Input(Plugin):

    def start(self, data=None, *, encoding='utf8'):
        self.data = data
        self.encoding = encoding
        self.proc.ready = asyncio.Event()


    def connected(self, transport):
        self.proc.mio[0] = transport.get_pipe_transport(0)
        self.proc.ready.set()


    async def run(self):
        if self.data != None:
            await self.proc.write(self.data)
            await self.proc.write(None)


    @Plugin.export
    async def write(self, data, encoding='utf8'):
        self.start()
        await self.ready.wait()
        if data == None:
            self.mio[0].close()
            return
        if isinstance(data, str):
            data = data.encode(encoding)
        if not isinstance(data, io.IOBase):
            if isinstance(data, bytes) or isinstance(data, bytearray):
                data = io.BytesIO(data)
        while line:=data.readline(io.DEFAULT_BUFFER_SIZE):
            print(f'---------> {line}')
            self.mio[0].write(line)
            await asyncio.sleep(0)


    @Plugin.export
    def pause_writing(self):
        self.ready.clear()


    @Plugin.export
    def resume_writing(self):
        self.ready.set()


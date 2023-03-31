from ..mio import MioBase, MioStream
from .plugin import Plugin


class Log(Plugin):
    ''' Log the output to a stream (opened in binary mode) or a file given by a path
    '''
    def start(self, src, fd=1|2):
        self.fd = fd
        if fd not in [1,2,3]: raise ValueError(f"Invalid fd: {fd}, must be 1,2 or 3")
        if isinstance(src, str):
            self.fname = src
            self.stream = None
            raise NotImplementedError()
        else:
            self.fname = None
            self.stream = src if isinstance(src, MioBase) else MioStream(src)


    async def finalize(self):
        if self.fname != None:
            raise NotImplementedError()


    def fd_data(self, fd, data):
        if fd & self.fd: self.stream.write(data)


    def fd_closed(self, fd):
        if self.fname == None: return
        raise NotImplementedError()


    def fd_buffer(self, fd):
        if fd == self.fd: return self.stream

from print_ext import Printer, Line
from .plugin import Plugin


class Echo(Plugin):

    def start(self, fd=1|2, *, encoding='utf8', style=None, tag={}):
        self.fd = fd
        if fd not in [1,2,3]: raise ValueError(f"Invalid fd: {fd}, must be 1,2 or 3")
        self.style = style
        self.encoding = encoding
        self.tag = tag


    async def run(self):
        with self.proc.mio[self.fd].reader() as read:
            async for line in read.each_line(encoding=self.encoding):
                line = Line(style=self.style).insert(0, line)
                Printer().append(line, self.tag)


    def fd_buffer(self, fd):
        if self.fd == fd: return True

from .plugin import Plugin


class Lines(Plugin):
    ''' Collect all of the output into a list of lines and return that object.
    '''

    def start(self, fd=1|2, *, only=0, encoding='utf8'):
        self.fd = fd
        if fd not in [1,2,3]: raise ValueError(f"Invalid fd: {fd}, must be 1,2 or 3")
        self.only = only
        self.encoding = encoding


    def fd_buffer(self, fd):
        if fd == self.fd: return True

    
    async def run(self):
        self.lines = []
        with self.proc.mio[self.fd].reader() as read:
            async for line in read.each_line(encoding=self.encoding):
                self.lines.append(line)
                if len(self.lines) == self.only: break


    def result(self):
        return self.lines



class OneLine(Lines):

    def start(self, *args, row=0, **kwargs):
        self.row = row
        super().start(*args, only=row+1, **kwargs)


    def result(self):
        return None if len(self.lines) <= self.row else self.lines[self.row]

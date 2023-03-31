from .plugin import Plugin


class Watch(Plugin):

    def start(self, fd=1|2):
        self.fd = fd
        if fd not in [1,2,3]: raise ValueError(f"Invalid fd: {fd}, must be 1,2 or 3")

    def fd_buffer(self, fd):
        if self.fd == fd: return True

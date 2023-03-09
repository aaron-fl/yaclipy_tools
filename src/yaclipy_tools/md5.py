from .sys_tool import SysTool
from .config import Config
from .run import run, CmdNotFound


class Md5(SysTool):
    cmd = Config.var("An absolute pathname to the md5 command", 'md5')

    @classmethod
    def version(self):
        return str(self.run(self, '-x', or_else=''))

    def hash(self, file):
        for line in self.run(file, stdout=True):
            return line.split(' ')[-1]

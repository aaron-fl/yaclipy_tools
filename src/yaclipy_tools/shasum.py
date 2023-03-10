from .sys_tool import SysTool
from .config import Config


class Shasum(SysTool):
    cmd = Config.var("An absolute pathname to the shasum command", 'shasum')

    @classmethod
    def version(self):
        for line in self.__call__(self, '--version', stdout=True):
            return line
        
        
    def hash(self, file):
        for line in self(file, stdout=True):
            return line.split(' ')[0]

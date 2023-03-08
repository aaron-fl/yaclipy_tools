from .sys_tool import SysTool
from .config import Config
from .run import run, CmdNotFound

exe = Config.var("An absolute pathname to the shasum command", 'shasum')

class Shasum(SysTool):

    def version(self):
        for line in run(exe(), '--version', stdout=True):
            return line
        
        
    def hash(self, file):
        for line in run(exe(), file, stdout=True):
            return line.split(' ')[0]
    
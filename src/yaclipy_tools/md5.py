from .sys_tool import SysTool
from .config import Config
from .run import run, CmdNotFound

exe = Config.var("An absolute pathname to the md5 command", 'md5')

class Md5(SysTool):

    def version(self):
        return '0' if run(exe(), '-x', success=True) == 0 else ''

    
    def hash(self, file):
        for line in run(exe(), file, stdout=True):
            return line.split(' ')[-1]

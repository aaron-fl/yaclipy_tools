import sys
from .sys_tool import SysTool
from .config import Config


class Curl(SysTool):
    cmd = Config.var("An absolute pathname to the curl command", 'curl')

    @classmethod
    def version(self):
        for line in self.run(self, '--version', stdout=True):
            return line.split(' ')[1]


    def download(self, url, fname=None):
        ''' Download a file.

        Parameters:
            fname <path>
                Save the file here.  Otherwise, if fname is None, yield each downloaded line.
        '''
        if fname:
            self.run(url, '-o', fname)
        else:
            return self.run(url, stdout=True)

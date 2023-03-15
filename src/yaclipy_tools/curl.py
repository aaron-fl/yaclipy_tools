from .sys_tool import SysTool
from .config import Config


class Curl(SysTool):
    cmd = Config.var("An absolute pathname to the curl command", 'curl')

    @classmethod
    def version(self):
        for line in self.__call__(self, '--version', stdout=True):
            return line.split(' ')[1]


    def download(self, url, fname=None):
        ''' Download a file.

        Parameters:
            <url>
                The url to download
            <path>, fname<path> [None]
                Save the file here.  Otherwise, if fname is None, yield each downloaded line.
        '''
        if fname:
            self(url, '-o', fname)
        else:
            return self(url, stdout=True)

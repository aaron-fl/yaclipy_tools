import yaclipy as CLI
from . import SysTool


class Curl(SysTool):
    cmd = CLI.config_var("An absolute pathname to the curl command", 'curl')
    used_for = CLI.config_var("Why is this required?", "curl is required.")


    @classmethod
    async def get_version(self):
        line = await self.proc('--version').one()
        return line.split(' ')[1]


    def download(self, url, path=None, **kwargs):
        ''' Download a file.

        Parameters:
            <url>
                The url to download
            <path>, path=<path> | default=None
                Save the file here.  Otherwise, if fname is None, yield each downloaded line.
            encoding=<str> | default='utf8'
                If you are not downloading to a file then this specifies the format of the returned data.
                Specify encoding=None for binary data.
        '''
        if path:
            return self(url, '-o', path)
        else:
            return self(url).lines()

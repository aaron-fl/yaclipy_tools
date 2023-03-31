import yaclipy as CLI
from . import SysTool, OneLine


class Md5(SysTool):
    cmd = CLI.config_var("An absolute pathname to the md5 command", 'md5')
    used_for = CLI.config_var("Why is this required?", "md5 is required.")


    @classmethod
    async def get_version(self):
        return str(await self.proc('-x', or_else=''))


    async def hash(self, file):
        line = await self.using(OneLine(1))(file)
        return line.split(' ')[-1]

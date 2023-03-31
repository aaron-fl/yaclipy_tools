import yaclipy as CLI
from . import SysTool, ProcTask, OneLine


class Shasum(SysTool):
    cmd = CLI.config_var("An absolute pathname to the shasum command", 'shasum')
    used_for = CLI.config_var("Why is this required?", "shasum is required.")

    @classmethod
    async def get_version(self):
        return await self.proc.using(OneLine(1))('--version')
        
    
    async def hash(self, path):
        line = await self.using(OneLine(1))(path)
        return line.split(' ')[0]

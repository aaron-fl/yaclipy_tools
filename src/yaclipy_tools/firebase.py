import yaclipy as CLI
from print_ext import PrettyException
from .sys_tool import SysTool


class Firebase(SysTool):
    cmd = CLI.config_var("An absolute pathname to the firebase command", 'firebase')
    used_for = CLI.config_var("Why is this required?", "firebase is required.")

    @classmethod
    async def get_version(self):
        line = await self.proc('--version').one()
        return line


    @classmethod
    def init_once(self, version=0, project=''):
        self.project = project
        super().init_once(version)
        if project:
            self.proc_verified = self.proc_verified('--project', project)

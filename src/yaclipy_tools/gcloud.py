from print_ext import PrettyException, Printer
import yaclipy as CLI
from . import SysTool, OneLine, Lines


def parse_version(lines, version):
    for line in lines:
        line = line.lower()
        if not line.startswith(version): continue
        line = {k.strip():v[1:-1] for k,v in [x.split(':',1) for x in line[line.index('{')+1:].split(',')]}
        return line['major'] + '.' + line['minor']
    return ''



class GCloudProjectError(PrettyException):
    def __pretty__(self, print, **kwargs):
        print(f"gcloud is currently configured for gcp project \berr {self.cur_project}")
        print(f"Use `\b2 gcloud init\b ` or `\b2 gcloud config configurations activate\b ` to change the project to \b1 {self.want_project}", pad=1)
        for line in self.config_list:
            print(line)


    @staticmethod
    async def check(tool, want):
        line = await tool.proc.using(OneLine(1))('config', 'get-value', 'project')
        cur = line.strip()
        config_list = await tool.proc.using(Lines(1))('config', 'configurations', 'list')
        if cur != want:
            raise GCloudProjectError(cur_project=cur, want_project=want, config_list=config_list)



class GCloud(SysTool):
    cmd = CLI.config_var("An absolute pathname to the gcloud command", 'gcloud')
    used_for = CLI.config_var("Why is this required?", "gcloud is required.")
    
    @classmethod
    async def get_version(self):
        line = await self.proc.using(OneLine(1))('--version')
        return line.split(' ')[-1]
            

    @classmethod
    def init_once(self, version=0, project='', **kwargs):
        deps = [GCloudProjectError.check(self, project)] if project else []
        super().init_once(version, deps=deps, **kwargs)


    def k8s_credentials(self, *, region, cluster_name):
        ''' Set the default credentials for kubectl to use.

        Parameters:
            region <str>
                The region that the cluster is in.
            cluster_name <str>
                The name of the cluster
        '''
        return self('container', 'clusters', 'get-credentials', '--region', region, cluster_name)

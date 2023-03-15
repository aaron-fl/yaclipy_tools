from .sys_tool import SysTool
from .config import Config
from print_ext import PrettyException, Printer

def parse_version(lines, version):
    for line in lines:
        line = line.lower()
        if not line.startswith(version): continue
        line = {k.strip():v[1:-1] for k,v in [x.split(':',1) for x in line[line.index('{')+1:].split(',')]}
        return line['major'] + '.' + line['minor']
    return ''


class GCloudProjectSet(PrettyException):
    def pretty(self, **kwargs):
        p = Printer()
        p(f"gcloud is currently configured for gcp project \berr {self.cur_project}")
        p(f"Use `\b2 gcloud init\b ` or `\b2 gcloud config configurations activate\b ` to change the project to \b1 {self.want_project}", pad=1)
        p(self.config_list)
        return p



class GCloud(SysTool):
    cmd = Config.var("An absolute pathname to the gcloud command", 'gcloud')

    @classmethod
    def version(self):
        for line in self.__call__(self, '--version', stdout=True):
            return line.split(' ')[-1]


    @classmethod
    def init_once(self, project_name='', version='0'):
        super().init_once(version)
        if not project_name: return
        # Verify the project_name
        for line in self.__call__(self, 'config', 'get-value', 'project', stdout=True):
            cur_project = line.strip()
            config_list = self.__call__(self, 'config', 'configurations', 'list', stdout='raw').decode('utf8')
            if cur_project != project_name:
                raise GCloudProjectSet(cur_project=cur_project, want_project=project_name, config_list=config_list)
            return


    def k8s_credentials(self, *, region, cluster_name):
        ''' Set the default credentials for kubectl to use.

        Parameters:
            region <str>
                The region that the cluster is in.
            cluster_name <str>
                The name of the cluster
        '''
        self('container','clusters','get-credentials','--region', region, cluster_name)

import yaclipy as CLI
from .sys_tool import SysTool


def _parse_version(lines, version):
    for line in lines:
        line = line.lower()
        if not line.startswith(version): continue
        line = {k.strip():v[1:-1] for k,v in [x.split(':',1) for x in line[line.index('{')+1:].split(',')]}
        return line['major'] + '.' + line['minor']
    return ''


class Kubectl(SysTool):
    cmd = CLI.config_var("An absolute pathname to the kubectl command", 'kubectl')
    used_for = CLI.config_var("Why is this required?", "kubectl is required.")

    @classmethod
    async def get_version(self):
        return _parse_version(await self.proc('version').lines(), 'client')


    async def server_version(self):
        ''' The version of the kubernetes cluster
        '''
        return _parse_version(await self('version').lines(), 'server')

    
    def apply(self, data_or_path):
        ''' Apply the yaml file.

        Parameters:
            <path>
                A path to a yaml file, or a dictionary of data
        '''
        if isinstance(data_or_path, dict):
            path = f'local/kube_apply_{hex(abs(hash(data_or_path)))}.yaml'
            with open() as f:
                yaml.dump(data_or_path, f)
            data_or_path = path
        return self('apply', '-f', data_or_path)

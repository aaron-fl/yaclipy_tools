from .sys_tool import SysTool
from .config import Config


def _parse_version(lines, version):
    for line in lines:
        line = line.lower()
        if not line.startswith(version): continue
        line = {k.strip():v[1:-1] for k,v in [x.split(':',1) for x in line[line.index('{')+1:].split(',')]}
        return line['major'] + '.' + line['minor']
    return ''


class Kubectl(SysTool):
    cmd = Config.var("An absolute pathname to the kubectl command", 'kubectl')

    @classmethod
    def version(self):
        return _parse_version(self.__call__(self, 'version', stdout=True), 'client')


    def server_version(self):
        ''' The version of the kubernetes cluster
        '''
        return _parse_version(self('version', stdout=True), 'server')

    
    def apply(self, filename):
        ''' Apply the yaml file.

        Parameters:
            <path>
                A yaml file to apply
        '''
        return self('apply', '-f', filename)
        
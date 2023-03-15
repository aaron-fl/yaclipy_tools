from print_ext import PrettyException
from .sys_tool import SysTool
from .config import Config

class DockerNotRunning(PrettyException): pass

class Docker(SysTool):
    cmd = Config.var("An absolute pathname to the docker command", 'docker')

    @classmethod
    def version(self):
        for line in self.__call__(self, '--version', stdout=True):
            return line.split(',')[0].split(' ')[2]
        
    @classmethod
    def init_once(self, *args):
        super().init_once(*args)
        try:
            self.__call__(self, 'images', '-q')
        except:
            raise DockerNotRunning(msg=f"The Docker demon is not running.  \berr Start docker desktop\b  and try again.")


    def image_id(self, image):
        ''' Return the docker ID for the given image or None if the image wasn't found.

        Parameters:
            <docker_image>
                The docker image name
        '''
        imgs = list(self('images', '-q', image, stdout=True))
        if not imgs: return None
        assert(len(imgs) == 1), f"Multiple images {imgs}"
        return imgs[0]

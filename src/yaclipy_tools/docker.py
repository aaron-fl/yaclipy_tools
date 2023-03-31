import json, asyncio
import yaclipy as CLI
from print_ext import PrettyException
from . import SysTool


class DockerNotRunning(PrettyException):
    @staticmethod
    async def check(tool):
        try:
            await tool.proc('images', '-q')
        except:
            raise DockerNotRunning(msg=f"The Docker demon is not running.  \berr Start docker desktop\b  and try again.")


class Docker(SysTool):
    cmd = CLI.config_var("An absolute pathname to the docker command", 'docker')
    used_for = CLI.config_var("Why is this required?", "docker is required.")
    
    @classmethod
    async def get_version(self):
        line = await self.proc('--version').one()
        return line.split(',')[0].split(' ')[2]


    @classmethod
    def init_once(self, *args, **kwargs):
        check_task = asyncio.create_task(DockerNotRunning.check(self))
        super().init_once(*args, deps=[check_task], **kwargs)


    def image_id(self, image):
        ''' Return the docker ID for the given image or None if the image wasn't found.

        Parameters:
            <docker_image>
                The docker image name
        '''
        return self('images', '-q', image).one()


    async def containers(self):
        ''' Get a list of all the containers.
        '''
        return [json.loads(line) for line in await self('container', 'ls', '-a', '--format', '{{json .}}').lines()]

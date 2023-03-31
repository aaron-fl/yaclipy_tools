import os, asyncio
from print_ext import PrettyException
#from .run import run, CmdNotFound
from .proc_task import ProcTask, Plugin
from .singleton import Singleton


class DepCheck(Plugin):
    def start(self, deps):
        self.deps = deps

    async def prepare(self):
        results = await asyncio.gather(*self.deps, return_exceptions=True)
        excs = [r for r in results if isinstance(r, Exception)]
        if len(excs) == 1: raise excs[0]
        if len(excs) > 1: raise Exception(excs) # 3.11 GroupException



class MissingTool(PrettyException):
    def __pretty__(self, print, **kwargs):
        if hasattr(self.tool, 'used_for') and (msg:=self.tool.used_for()):
            print(msg)
        print(f"\b1 {self.tool.__mro__[1].__name__}\b  requires version >= \b2 {self.need}")
        if not self.got:
            print('\berr No version was found.')
        else:
            print(f'Version \berr {self.got}\b  was found.')
        import platform
        pfm = 'install_help_' + platform.platform().lower().split('-')[0]
        self.tool.install_help_generic(print)
        if hasattr(self.tool, pfm): getattr(self.tool, pfm)(print)



class SysTool(metaclass=Singleton):

    @classmethod
    async def get_version(self):
        raise FileNotFoundError()


    @classmethod
    def install_help_generic(self, print):
        pass


    @classmethod
    def init_once(self, version=0, plugins=[], deps=[], **kwargs):
        self.version = asyncio.create_task(self._verify(str(version)))
        deps.append(self.version)
        self.deps = deps
        self.proc = ProcTask().use(*plugins, **kwargs)(self.cmd())
        self.proc_verified = self.proc.use(DepCheck(deps))


    @classmethod
    async def _verify(self, version):
        try:
            got = await self.get_version()
        except FileNotFoundError as e:
            got = ''
        got_version = tuple(map(int, got.split('.'))) if got else [-1]
        for n, g in zip(map(int, version.split('.')), got_version):
            if g > n: break
            if n == g: continue
            # Version mismatch
            raise MissingTool(tool=self, need=version, got=got)
        return got_version


    async def ensure(self):
        return await asyncio.gather(*self.deps)


    def use(self, *args, **kwargs):
        return self.proc_verified.use(*args, **kwargs)


    def __call__(self, *args, **kwargs):
        return self.proc_verified(*args, **kwargs)

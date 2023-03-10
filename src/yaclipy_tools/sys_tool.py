import os
from print_ext import PrettyException, Text
from .run import run, CmdNotFound
from .singleton import Singleton

class MissingTool(PrettyException): pass



class SysTool(metaclass=Singleton):

    @classmethod
    def version(self):
        return ''

    @classmethod
    def install_help(self, t):
        return t
        
    @classmethod
    def init_once(self, version='0'):
        try:
            got = self.version()
        except CmdNotFound:
            got = ''
        for n, g in zip(map(int, version.split('.')), map(int, got.split('.')) if got else [-1]):
            if g > n: break
            if n == g: continue
            # Version mismatch
            t = Text(f"\b1 {self.__class__.__name__} requires version >= \b2 {version}.\n")
            if not got:
                t('\vNo version was found.')
            else:
                t(f"\vVersion \b2 {got}\b  was found.")
            raise MissingTool(msg=self.install_help(t))


    def __init__(self, verbose=0, **kwargs):
        self.verbose = verbose
        

    def run(self, *args, **kwargs):
        try:
            verbose = self.verbose
        except AttributeError: # self might be a class calling version()
            verbose = 0
        kwargs.setdefault('verbose', verbose)
        return run(self.cmd(), *args, **kwargs)

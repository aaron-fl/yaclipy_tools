import os, sys, logging
from print_ext import PrettyException, Text
from subprocess import run, Popen, PIPE
from .run import CmdNotFound

log = logging.getLogger('syscmd')

class MissingTool(PrettyException): pass


class Singleton(type):
    def __call__(cls, *args):
        if not hasattr(cls, '_instances'): cls._instances = {}
        if args not in cls._instances:
            cls._instances[args] = super(Singleton, cls).__call__(*args)
        return cls._instances[args]


class SysTool(metaclass=Singleton):
    def __init__(self, version='0'):
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
        

    def version(self):
        return ''


    def install_help(self, t):
        return t
        

import yaclipy as CLI
from print_ext import Printer
from pathlib import Path
from . import SysTool


class GraphViz(SysTool):
    cmd = CLI.config_var("An absolute pathname to the `dot` command", 'dot', lambda p: Path(p))
    used_for = CLI.config_var("Why is this required?", "graphviz is required.")

    @classmethod
    async def get_version(self):
        Printer().pretty(self.proc)
        line = await self.proc(self.cmd(), '-V').one(2)
        line = line.lower().split(' ')
        return line[line.index('version')+1]


    @classmethod
    def install_help_macos(self, print):
        print("Install using brew:")
        print("  $ brew install graphviz")


    @classmethod
    def install_help_generic(self, print):
        print("https://graphviz.org/download/")


    @classmethod
    def init_once(self, *args, **kwargs):
        super().init_once(*args, **kwargs)
        self.cmd_base = Path(self.cmd()).parent
        self.proc.cmd = tuple()
        self.proc_verified.cmd = tuple()


    def __call__(self, name, *args, **kwargs):
        cmd = Path(self.cmd_base)/name
        print(f"CMD: {cmd}")
        return self.proc_verified(cmd, *args, **kwargs)


    def gen(self, dot, fin, *args, path=None, type='png', **kwargs):
        fin = None if fin == '-' else Path(fin)
        fout = fin.parent/f"{fin.stem}.{type}" if path == None else Path(path)
        cmd = self(dot, *args, f'-T{type}', f'-o{fout}', **kwargs)
        return cmd(fin) if fin else cmd

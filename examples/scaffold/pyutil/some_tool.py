import os
from print_ext import print
from yaclipy_tools.config import Config

class SomeTool():
    data_path = Config.var("A path to some data", lambda: os.path.abspath('local/data'))

    def do_something(self):
        print(f"Doing something to \b1 {SomeTool.data_path()}")

import pytest
from print_ext import print
from yaclipy_tools.sys_tool import MissingTool
from yaclipy_tools.nginx import Nginx
from yaclipy_tools.run import CmdRunError

def _nginx(**kwargs):
    try:
        kwargs.setdefault('verbose',4)
        return Nginx('1.20', **kwargs)
    except MissingTool as e:
        print.pretty(e)
        raise e
        pytest.skip("nginx not installed")



def test_nginx_config():
    nginx = _nginx()
    print.pretty(nginx.cfg_tree)
    assert('pid local/nginx/nginx.pid' in nginx.cfg_tree)
    #assert(nginx.cfg_tree == {})


def test_nginx_run():
    nginx = _nginx()
    nginx.start()
    print("RUNNING")
    nginx.stop()

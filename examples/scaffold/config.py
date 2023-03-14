from contextlib import suppress
from yaclipy_tools.config import Config


prefix = Config.var("A target-specific prefix", '')
name = Config.var("The name of the project", 'scaffold')
port = Config.var("Backend server port", 9000)


@Config.target(mutex='test')
def prod():
    prefix('prod')
    port(9001)


@Config.target(mutex='prod')
def test():
    prefix('test')
    port(9009)


with suppress(ImportError): import local.config

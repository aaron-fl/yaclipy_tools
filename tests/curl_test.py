from print_ext import print
from yaclipy_tools.sys_tool import MissingTool
from yaclipy_tools.curl import Curl


def _curl():
    try:
        return Curl('7', verbose=4)
    except MissingTool as e:
        print.pretty(e)
        pytest.skip("curl not installed")


def test_curl_download():
    curl = _curl()
    lines = list(curl.download('https://raw.githubusercontent.com/nginx/nginx/master/conf/mime.types'))
    assert('types {' in lines)

    

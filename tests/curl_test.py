import pytest
from yaclipy_tools.all import Curl
from .testutil import get_tool


@pytest.mark.asyncio
async def test_curl_download_lines():
    curl = await get_tool(Curl('7'))
    v = await curl.download('https://raw.githubusercontent.com/nginx/nginx/master/conf/mime.types')
    print(v)
    assert('types {' in v)



@pytest.mark.asyncio
async def test_curl_download_file(tmp_path):
    curl = await get_tool(Curl('7'))
    await curl.download('https://raw.githubusercontent.com/nginx/nginx/master/conf/mime.types', path=tmp_path/'mime.types')
    with open(tmp_path/'mime.types') as f:
        all = f.read()
        print(all)
        assert('types {' in all)

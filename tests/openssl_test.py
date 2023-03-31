import pytest
from yaclipy_tools.all import OpenSSL
from .testutil import get_tool



@pytest.mark.asyncio
async def test_openssl_hash():
    ossl = await get_tool(OpenSSL('3'))
    assert(await ossl.hash('tests/echo.py') == '452cb1c5aab6b2b967b163e7efeda64963d295dda764ca84f21c85cae77351f3')
    assert(await ossl.hash('tests/doesntexist.py') == '')



@pytest.mark.asyncio
async def test_openssl_rand(tmp_path):
    ossl = await get_tool(OpenSSL('3'))
    rv = await ossl.rand(bytes=1)
    print(rv)
    assert(len(rv) == 2)
    await ossl.rand(path=tmp_path / 'x.txt')
    with open(tmp_path / 'x.txt') as f:
        assert(len(f.read()) == 2*32+1)



@pytest.mark.asyncio
async def test_openssl_cert(tmp_path):
    ossl = await get_tool(OpenSSL('3'))
    resp = await ossl.cert(prefix=tmp_path/'test', cn='common', ca=None, san=['127.0.0.1', '0:0:0:0:0:0:0:1', 'localhost'], client=False, force=False, askpass=False, days=1)
    assert(resp == {'O': 'yaclipy-tools', 'CN': 'common'})
    resp = await ossl.cert_inspect(tmp_path/'test', '-issuer')
    assert(resp == {'O': 'yaclipy-tools', 'CN': 'common'})

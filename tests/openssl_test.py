import pytest
from print_ext import print
from yaclipy_tools.sys_tool import MissingTool
from yaclipy_tools.openssl import OpenSSL


def _openssl():
    OpenSSL.cmd('/opt/homebrew/opt/openssl/bin/openssl')
    try:
        return OpenSSL('3', verbose=4)
    except MissingTool as e:
        print.pretty(e)
        pytest.skip("openssl not installed")



def test_openssl_hash():
    ossl = _openssl()
    assert(ossl.hash('tests/echo.py') == '3eaede45287f555c1d0bcf117f7cb6bf35ddee9ea6d2abc7de25dfa9f18e0e9f')
    assert(ossl.hash('tests/doesntexist.py') == '')



def test_openssl_rand(tmp_path):
    ossl = _openssl()
    assert(len(ossl.rand(bytes=1)) == 2)
    ossl.rand(fname=tmp_path / 'x.txt')
    with open(tmp_path / 'x.txt') as f:
        assert(len(f.read()) == 2*32+1)



def test_openssl_cert(tmp_path):
    ossl = _openssl()
    resp = ossl.cert(prefix=tmp_path/'test', cn='common', ca=None, san=['127.0.0.1', '0:0:0:0:0:0:0:1', 'localhost'], client=False, force=False, askpass=False, days=1)
    assert(resp == {'O': 'yaclipy-tools', 'CN': 'common'})
    resp = ossl.cert_inspect(tmp_path/'test', '-issuer')
    assert(resp == {'O': 'yaclipy-tools', 'CN': 'common'})

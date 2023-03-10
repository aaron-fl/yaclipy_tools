from yaclipy_tools.md5 import Md5

def test_md5():
    md5 = Md5()
    assert(md5.hash('tests/echo.py') == '4200d5caa042d2ab5ea4924ef03495cb')

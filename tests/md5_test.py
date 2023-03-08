from yaclipy_tools.md5 import Md5

def test_md5():
    md5 = Md5()
    assert(md5.hash('tests/echo.py') == 'ceb05d41a0c6a90fc58c5f39ed841b9f')

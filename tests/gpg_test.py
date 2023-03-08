from print_ext import print
from yaclipy_tools.run import CmdRunError
from yaclipy_tools.gpg import GPG

def test_gpg():
    gpg = GPG('2.3')
    assert(gpg.import_key('x') == None)
    


if __name__=='__main__':
    for u in GPG('2.3').list_users():
        print(u)
    GPG('2.3').genkey()

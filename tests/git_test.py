from print_ext import print
from yaclipy_tools.run import CmdRunError
from yaclipy_tools.git import Git

def test_git():
    git = Git()
    assert(git.name == 'yaclipy_tools')
    assert(len(git.current_commit()) == 40)
    assert(git.current_branch() == 'main')


def test_git_status():
    git = Git()
    print.pretty(git.status())


def test_git_list():
    git = Git()
    print.pretty(list(git.list('*.py', invert=True)))

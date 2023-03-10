from print_ext import print
from yaclipy_tools.git import Git
from yaclipy_tools.run import run
from yaclipy_tools.orphan_branch import OrphanBranch

def _write_file(git, fname, contents):
    with (git.repo/fname).open('a') as f:
        f.write(contents)

def _setup_remote(tmp_path):
    (tmp_path/'remote').mkdir()
    git = Git(repo=tmp_path/'remote', verbose=4)
    git('init')
    _write_file(git, 'f1', 'f1 says hi')
    git('add', tmp_path/'remote/f1')
    git('commit', '-am', '1st')
    git('branch','-m','main')
    git('checkout','-b','other')
    return git

def _setup(tmp_path):
    remote = _setup_remote(tmp_path)
    run('git', 'clone', tmp_path/'remote', tmp_path/'clone1', verbose=4)
    run('git', 'clone', tmp_path/'remote', tmp_path/'clone2', verbose=4)
    oph1 = OrphanBranch(local=tmp_path/'clone1'/'static', remote=tmp_path/'remote'/'rstatic', repo=tmp_path/'clone1', verbose=4)
    oph2 = OrphanBranch(local=tmp_path/'clone1'/'static', remote=tmp_path/'remote'/'rstatic', repo=tmp_path/'clone1', verbose=4)
    return remote, oph1, oph2


def test_orphan(tmp_path):
    remote, oph1, oph2 = _setup(tmp_path)
    _write_file(oph1.git, 'f2', 'f2 contents')
    oph1.git('add', '.')
    oph1.git('commit', '-am', 'f2')
    _write_file(oph1.git, 'f3', 'f2 contents')
    _write_file(oph1.git, 'f2', 'change it')
    print.pretty(oph1.git.status())
    oph1.initialize()


    assert(False)
    
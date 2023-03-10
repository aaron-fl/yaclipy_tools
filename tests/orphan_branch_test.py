from print_ext import print
from yaclipy_tools.git import Git
from yaclipy_tools.run import run
from yaclipy_tools.orphan_branch import OrphanBranch

def _setup_remote(tmp_path):
    (tmp_path/'remote').mkdir()
    git = Git(repo=tmp_path/'remote', verbose=4)
    git.run('init')
    with (tmp_path/'remote/f1').open('w') as f:
        f.write('hi')
    git.run('commit', '-am', '1st')
    git.run('branch','-m','main')
    git.run('checkout','-b','other')


def _setup(tmp_path):
    remote = _setup_remote(tmp_path)
    run('git', 'clone', tmp_path/'remote', tmp_path/'clone1')
    run('git', 'clone', tmp_path/'remote', tmp_path/'clone2')
    oph1 = OrphanBranch(local=tmp_path/'clone1'/'static', remote=tmp_path/'remote'/'rstatic', repo=tmp_path/'clone1', verbose=4)
    oph2 = OrphanBranch(local=tmp_path/'clone1'/'static', remote=tmp_path/'remote'/'rstatic', repo=tmp_path/'clone1', verbose=4)
    return remote, oph1, oph2


def test_orphan(tmp_path):
    remote, oph1, oph2 = _setup(tmp_path)
    
    print.pretty(remote.status())


    assert(False)
    
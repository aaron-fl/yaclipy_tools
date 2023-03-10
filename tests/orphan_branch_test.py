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
    _write_file(git, 'abc', 'abcd')
    git('add', 'abc')
    git('commit', '-am', '2nd')
    git('branch','-m','main')
    git('checkout','-b','other')
    return git



def test_orphan(tmp_path):
    remote = _setup_remote(tmp_path)
    run('git', 'clone', '-b','main', tmp_path/'remote', tmp_path/'clone1', verbose=4)
    oph1 = OrphanBranch('static', repo=tmp_path/'clone1', verbose=4)

    _write_file(oph1.git, 'f2', 'f2 contents')
    oph1.git('add', '.')
    oph1.git('commit', '-am', 'f2')
    _write_file(oph1.git, 'f3', 'f2 contents')
    _write_file(oph1.git, 'f2', 'change it')
    with (oph1.git.repo/'f2').open() as f:
        assert(f.read() == 'f2 contentschange it')
    print.pretty(oph1.git.status())
    #(oph1.git.repo/'static').mkdir()
    oph1.ensure()
    with (oph1.git.repo/'f2').open() as f:
        assert(f.read() == 'f2 contentschange it')

    # Now clone when static already exists
    print("\v\v\v\v\vORPHAN 2\v\v\v")
    run('git', 'clone', '-b','main', tmp_path/'remote', tmp_path/'clone2', verbose=4)
    oph2 = OrphanBranch('static', checkout_path='local/tmp/static', repo=tmp_path/'clone2', verbose=4)
    assert( not (oph2.git.repo/'local/tmp/static/.gitignore').is_file())
    oph2.ensure()
    assert( (oph2.git.repo/'local/tmp/static/.gitignore').is_file())
    


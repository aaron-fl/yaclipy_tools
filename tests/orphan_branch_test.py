import pytest
from print_ext import print, pretty
from yaclipy_tools.git import Git
from yaclipy_tools.run import run, CmdRunError
from yaclipy_tools.orphan_branch import OrphanBranch, FStat, DeletedFiles

def _write_file(git, fname, contents=None):
    contents = contents or f"Contents of {fname}"
    (git.repo/fname).parent.mkdir(exist_ok=True)
    with (git.repo/fname).open('a') as f:
        f.write(contents)

def _setup_remote(tmp_path):
    (tmp_path/'remote').mkdir()
    git = Git(repo=tmp_path/'remote', verbose=4)
    git('init')
    _write_file(git, 'f1', 'f1 says hi')
    git('add', 'f1')
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
    



def test_orphan_files(tmp_path):
    remote = _setup_remote(tmp_path)
    run('git', 'clone', '-b','main', tmp_path/'remote', tmp_path/'clone1', verbose=4)
    oph1 = OrphanBranch('static', repo=tmp_path/'clone1', verbose=4)
    oph1.ensure()
    print('\v\v\v\v\v\v\v')
    _write_file(oph1.branch_git, '.gitignore', '*.gpg')
    _write_file(oph1.branch_git, 'afile.py')
    _write_file(oph1.branch_git, 'bfile.py')
    _write_file(oph1.branch_git, 'afix/jim.txt.gpg')
    oph1.branch_git('status')
    oph1.branch_git('add', '.')
    oph1.branch_git('commit', '-am', '3rd')
    _write_file(oph1.branch_git, 'afox.txt')
    oph1.branch_git('add', '.')
    _write_file(oph1.branch_git, 'afix/tim.png')
    (oph1.branch_git.repo/'bfile.py').unlink()
    for f in sorted(oph1.files()):
        print(f.flags, pretty(f))
    assert([(str(f.fname),f.flags) for f in sorted(oph1.files())] == [('afix/jim.txt.gpg',FStat.NONE), ('.gitignore',FStat.TRACKED), ('afile.py', FStat.TRACKED), ('afox.txt',FStat.TRACKED), ('bfile.py',FStat.TRACKED|FStat.REM)])
    # Clone in another repo
    run('git', 'clone', '-b','main', tmp_path/'remote', tmp_path/'clone2', verbose=4)
    oph2 = OrphanBranch('static', repo=tmp_path/'clone2', verbose=4)
    oph2.ensure()
    assert([(str(f.fname),f.flags) for f in sorted(oph2.files())] == [('.gitignore',FStat.TRACKED)])

    with pytest.raises(DeletedFiles):
        oph1.commit()
    oph1.commit(force=True)
    oph1.push()
    oph1.pull()

    # Create some conflicting files on oph2
    _write_file(oph2.branch_git, 'afile.py','differnt')
    
    try:
        oph2.pull()
    except CmdRunError as e:
        print.pretty(e)
    oph2.commit()
    try:
        oph2.pull()
    except CmdRunError as e:
        print.pretty(e)
        oph2.branch_git('status')
        for f in (oph2.branch_git.repo).iterdir():
            print(f'---> {f}')
        with (oph2.branch_git.repo/'afile.py').open() as f:
            print.card('\t',f.read())
    oph2.branch_git('add', 'afile.py')
    print('\v'*5)
    oph2.branch_git('rebase', '--continue', env={'GIT_EDITOR':'true'})
    
    #oph2.branch_git('status')
    #print('\v'*5)
    oph2.commit()
    oph2.push()


if __name__ == '__main__':
    from pathlib import Path
    import shutil
    tmp_dir = Path('local/pytest_tmp/test_orphan_files0')
    shutil.rmtree(tmp_dir)
    tmp_dir.mkdir()
    test_orphan_files(tmp_dir)

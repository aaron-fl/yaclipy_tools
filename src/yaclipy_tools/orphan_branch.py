from print_ext import PrettyException, Text, pretty
from pathlib import Path
from .git import Git
from enum import Flag, auto


class DeletedFiles(PrettyException):
    def pretty(self, **kwargs):
        return pretty(self.deleted)


class FStat(Flag):
    NONE = 0
    TRACKED = auto() # The file is tacked by git
    CONFLICT = auto() # The local and remote files are in conflict
    GPG = auto() # The file is currently encrypted
    REM = auto() # The file has been removed,
    NOEXIST = auto() # The file does not exist


class File():
    def __init__(self, fname, flags=FStat.NONE):
        self.fname = Path(fname)
        self.flags = flags


    def __str__(self):
        return str(self.fname)


    def __contains__(self, other):
        return other in self.flags


    def pretty(self):
        style = 'w,.'
        if FStat.CONFLICT in self: style = 'err'
        elif FStat.REM in self: style = 'm!'
        elif FStat.GPG in self and FStat.TRACKED not in self: style = 'g!'
        elif FStat.NOEXIST not in self and FStat.GPG in self: style = 'y_'
        elif FStat.TRACKED not in self and FStat.GPG not in self: style = 'w!;'
        icon = '💀' if FStat.REM in self else '🔒' if FStat.GPG in self else '  '
        return f'{icon}\b{style} {self}'


    def __eq__(self, other):
        return str(self.fname) == str(other)

    
    def __lt__(self, other):
        a = self.fname.parts
        b = other.fname.parts if isinstance(other, File) else other.parts if isinstance(other, Path) else str(other).split('/')
        if len(a) != len(b): return len(a) > len(b)
        i = 0
        while i < len(a) and a[i] == b[i]: i += 1
        return a[i] < b[i]


    def __and__(self, other):
        return other in self.flags


    def __bool__(self):
        return self.flags != None


    def matches(self, paths):
        for p in paths:
            if str(p).endswith('/'):
                if p == './' or str(self.fname).startswith(p): return p
            elif str(self.fname) == p: return p


    def secure_delete(self):
        rbytes = random.randbytes(self.fname.stat().st_size)
        with open(self.fname, 'wb') as f:
            f.write(rbytes)
        self.fname.unlink()



class FileList(list):

    def pretty(self, **kwargs):
        t = Text()
        for f in sorted(self):
            t(pretty(f), '\v')
        return t

    def add(self, name, flags):
        try:
            idx = self.index(name)
            f = self[idx]
            self[idx] = File(f.fname, f.flags | flags)
        except:
            self.append(File(name, flags))
            

    #def add(self, name, flags=0):
    #    if name.startswith('members/') or name in ['.gitignore', 'README.rst']: return
    #    f = self.get(name)         
    #    if name.endswith('.gpg') or name.endswith('.orig'):
    #        flags |= File.NOEXIST | (File.GPG if name.endswith('.gpg') else File.CONFLICT)
    #    if not f:
    #        f.flags = flags
    #        self.append(f)
    #    else:
    #        f.flags = (f.flags|flags) & (0xff^File.NOEXIST)


    def get(self, name):
        #n, ext = os.path.splitext(str(name))
        #if ext in ['.gpg', '.orig']: name = n
        #if name in self: return self[self.index(name)]
        #return File(name, -1)
        try:
            self[self.index(name)]
        except:
            return File(name, FStat.NONE)




class OrphanBranch():
    ''' This is a Git branch that gets --amended and updated with --force so that no revision control is used.
    '''
    def __init__(self, branch, *, checkout_path=None, remote='origin', repo='.', **kwargs):
        self.branch = branch
        self.remote = Path(remote)
        self.checkout_path = checkout_path or branch
        self.git = Git(repo=repo, **kwargs)
        self.branch_git = Git(repo=self.git.repo/self.checkout_path, **kwargs)

    
    def ensure(self):
        if self.branch_git.repo.is_dir():
            if not (self.branch_git.repo/'.git').is_dir():
                raise Exception(f"The directory {self.branch_git.repo} exists, but is not a git worktree.")
            if self.branch_git.name != self.branch:
                raise Exception(f"Wrong branch {self.branch_git.name} at {self.branch_git.repo}")
            return # It already exists
        if self.git('worktree', 'add', '--lock', self.checkout_path, self.branch, success=[0,128], msg=f"Checkout {self.branch} worktree to {self.checkout_path}") == 128:
            self._initialize()
            return self.ensure()


    def _initialize(self):
        if self.git('ls-remote', '--exit-code', '--heads', self.remote, self.branch, or_else=1) == 0:
            print(f"Doing nothing.  {self.branch} exists on {self.remote}")
            return
        self.git('status')
        cur_branch = self.git.current_branch()  
        cur_commit = self.git.current_commit()[:7]
        stashed = cur_commit in list(self.git('stash', 'push', stdout=True))[0]
        self.git('checkout','--orphan',self.branch)
        self.git('reset', '--hard')
        with (self.git.repo/'.gitignore').open('w') as f: f.write('')
        self.git('add', '.gitignore')
        self.git('commit', '-am', f"New orphan branch {self.branch!r}")
        self.git('push', '-u', self.remote, self.branch)
        self.git('switch', cur_branch)
        if stashed: self.git('stash', 'pop')



    def files(self):
        lst = FileList()
        for f in self.branch_git.list(): lst.add(f, FStat.TRACKED)
        for t,f in self.branch_git.status('--ignored', changes_only=True):
            print(f"--------- {t}  {f}")
            if 'D' in t: lst.add(f, FStat.REM)
            elif '!!' in t: lst.add(f, FStat.NONE)
        return lst



    def commit(self, force=False):
        if not force and (deleted:=[f for f in self.files() if FStat.REM in f]):
            raise DeletedFiles(deleted=deleted)
        self.branch_git('add','-A')
        self.branch_git('commit', '-am', 'orphan')


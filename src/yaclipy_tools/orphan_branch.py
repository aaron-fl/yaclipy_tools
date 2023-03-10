from pathlib import Path
from .git import Git

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
        trees = self.git('worktree', 'list', '--porcelain', '-z',stdout='raw').decode('utf8').split('\0')
        for tree in trees:
            print(f"TREE: {tree}")
        if self.branch_git.repo.is_dir():
            print("ALREADY A DIRECTORY")
            if not (self.branch_git.repo/'.git').is_dir():
                raise Exception(" NO GIT DIRECTORY")
            if self.branch_git.name != self.branch:
                raise Exception(f"Wrong branch {self.branch_git.name} at {self.branch_git.repo}")
            return # It already exists
        if self.git('worktree', 'add', '--lock', self.checkout_path, self.branch, success=[0,128], msg=f"Checkout {self.branch} worktree to {self.checkout_path}") == 128:
            print(f"Branch does not exist.  Create it and try again")
            self.initialize()
            return self.ensure()
        print("ADDED __________________")
        for tree in self.git('worktree', 'list', '--porcelain', '-z',stdout='raw').decode('utf8').split('\0'):
            print(f"TREE: {tree}")
        self.git('status')


    def initialize(self):
        if self.git('ls-remote', '--exit-code', '--heads', self.remote, self.branch, or_else=1) == 0:
            print(f"Doing nothing.  {self.branch} exists on {self.remote}")
            return
        print(f"Initializing orphan {self.branch}")
        self.git('status')
        cur_branch = self.git.current_branch()  
        cur_commit = self.git.current_commit()[:7]
        stashed = cur_commit in list(self.git('stash', 'push', stdout=True))[0]
        print(f"stashed? {stashed}  {cur_commit}")
        self.git('checkout','--orphan',self.branch)
        self.git('reset', '--hard')
        with (self.git.repo/'.gitignore').open('w') as f: f.write('')
        self.git('add', '.gitignore')
        self.git('commit', '-am', f"New orphan branch {self.branch!r}")
        self.git('push', '-u', self.remote, self.branch)
        self.git('switch', cur_branch)
        if stashed: self.git('stash', 'pop')

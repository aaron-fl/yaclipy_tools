from .git import Git

class OrphanBranch():
    ''' This is a Git branch that gets --amended and updated with --force so that no revision control is used.
    '''
    def __init__(self, *, checkout_path, remote, branch, repo='.', **kwargs):
        self.git = Git(repo=repo, **kwargs)
        self.checkout_path, self.remote, self.branch = checkout_path, remote, branch

    
    def ensure(self):
        self.git('worktree', 'add', self.local, self.remote, msg=f"Creating {self.local} worktree")


    def initialize(self):
        if self.git('ls-remote', '--heads', self.remote, self.branch, or_else=1) == 0:
            print(f"Doing nothing.  {self.branch} exists on {self.remote}")
            return
        print(f"Initializing orphan {self.branch}")
        


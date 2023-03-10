from .git import Git

class OrphanBranch():
    ''' This is a Git branch that gets --amended and updated with --force so that no revision control is used.
    '''
    def __init__(self, *, local, remote, repo='.', **kwargs):
        self.git = Git(repo=repo, **kwargs)
        self.local, self.remote = local, remote

    
    def ensure(self):
        self.git('worktree', 'add', self.local, self.remote, msg=f"Creating {self.local} worktree")




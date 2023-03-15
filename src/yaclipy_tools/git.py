import sys, os, enum
from pathlib import Path
from .sys_tool import SysTool
from .config import Config


class Git(SysTool):
    cmd = Config.var("An absolute pathname to the git command", 'git')

    @classmethod
    def version(self):
        for line in super().__call__(self, '--version', stdout=True):
            return line.split(' ')[2]


    def __init__(self, repo='.', **kwargs):
        self.repo = Path(repo)
        super().__init__(**kwargs)


    def __bool__(self):
        return bool(self.name)


    def __call__(self, *args, **kwargs):
        return super().__call__('-C', self.repo, *args, **kwargs)


    @property
    def name(self):
        ''' The name of the repo based on either the remote name or the local name.
        '''
        if not hasattr(self, '_name'):
            l = list(self('config', '--get', 'remote.origin.url', stdout=True, msg=f'{self.repo}: Origin', or_else=['']))[0]
            if not l:
                l = list(self('rev-parse','--show-toplevel', stdout=True, msg=f'{self.repo}: Name', or_else=['']))[0]
            self._name = os.path.splitext(os.path.basename(l))[0]
        return self._name


    def current_commit(self):
        ''' The current commit hash
        '''
        return list(self('rev-parse','HEAD', msg=f'{self.repo}: Current commit', stdout=True))[0]


    def status(self, *args, changes_only=False):
        ''' A list of changes [(code, file)]

        Parameters:
            changes_only <bool> [False]
                If False, then check if we need to push `: ` or pull `; `
        '''
        changes = [x for x in self('status', '-z', *args, stdout='raw', msg=f'{self.repo}: Status').decode('utf8').split('\0') if x]
        changes = [(k[:2],Path(k[3:])) for k in changes]
        if changes or changes_only: return changes
        if list(self('fetch', '--dry-run', stdout=True, msg=f'{self.repo}: Check pull')):
            return [('; ','Need to pull')]
        if list(self('status', '-sb', stdout=True, msg=f'{self.repo}: Check push'))[0].split('[')[-1].startswith('ahead'):
            return [(': ','Need to push')] 
        return []


    def current_branch(self):
        ''' The name of the current branch.
        '''
        return list(self('symbolic-ref', '--short', 'HEAD', stdout=True, msg=f'{self.repo}: Branch'))[0]


    def up_to_date(self):
        ''' Check `status()` to see if we are up-to-date.
        '''
        return not bool(self.status())


    def list(self, *pattern, invert=False):
        ''' An iterator using `ls-files` to list files based on .gitignore rules.
        '''
        for p in self('ls-files', *pattern, *(['--other'] if invert else []), stdout=True, msg=f'{self.repo}: List'):
            yield Path(p)



def rebase_ff(base, ontop, *, repo='.', verbose__v=False):
    ''' Rebase and then ff merge.  New commits from `ontop` will be applied to `base`.

    Parameters:
        <branch>, --base <branch>  *required* 
            The branch to apply changes to.
        <branch>, --ontop <branch> *required*
            The branch containing new commits.
        --repo <path>
            The repository to work on ('.' by default).
        --verbose, -v
            Use up to three -vvv for lots of verbosity.
    '''
    git = Git(repo=repo, verbose=int(verbose__v))
    git('rebase', base, ontop)
    git('switch', base)
    git('merge', '--ff-only', ontop)

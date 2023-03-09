import sys, os
from pathlib import Path
from .sys_tool import SysTool
from .config import Config


class Git(SysTool):
    cmd = Config.var("An absolute pathname to the git command", 'git')

    @classmethod
    def version(self):
        for line in self.run(self, '--version', stdout=True):
            return line.split(' ')[2]


    def __init__(self, repo='.'):
        self.repo = Path(repo)


    def __bool__(self):
        return bool(self.name)


    @property
    def name(self):
        if not hasattr(self, '_name'):
            l = list(self.run('-C', self.repo, 'config', '--get', 'remote.origin.url', stdout=True, msg=f'{self.repo}: Origin', or_else=['']))[0]
            if not l:
                l = lines(self.run('-C',self.repo,'rev-parse','--show-toplevel', stdout=True, msg=f'{self.repo}: Name', or_else=['']))[0]
            self._name = os.path.splitext(os.path.basename(l))[0]
        return self._name


    def current_commit(self):
        return list(self.run('-C',self.repo,'rev-parse','HEAD', msg=f'{self.repo}: Current commit', stdout=True))[0]


    def status(self, changes_only=False):
        changes = [x for x in self.run('-C', self.repo, 'status', '-z', stdout='raw', msg=f'{self.repo}: Status').decode('utf8').split('\0') if x]
        changes = [(k[:2],k[3:]) for k in changes]
        if changes or changes_only: return changes
        if list(self.run('-C', self.repo, 'fetch', '--dry-run', stdout=True, msg=f'{self.repo}: Check pull')):
            return [('  ','Need to pull')]
        if list(self.run('-C', self.repo, 'status', '-sb', stdout=True, msg=f'{self.repo}: Check push'))[0].split('[')[-1].startswith('ahead'):
            return [('  ','Need to push')] 
        return []


    def current_branch(self):
        return list(self.run('-C', self.repo, 'symbolic-ref', '--short', 'HEAD', stdout=True, msg=f'{self.repo}: Branch'))[0]


    def up_to_date(self):
        return not bool(self.status())


    def list(self, *pattern, invert=False):
        return self.run('-C', self.repo, 'ls-files', *pattern, *(['--other'] if invert else []), stdout=True, msg=f'{self.repo}: List')


    def pull_rebase(self, *args):
        self.run('-C', self.repo, 'pull', '--rebase', *args)


    def push(self, *args, force=False):
        self.run('-C', self.repo, 'push', *(['--force-with-lease'] if force else []), *args)



def status(repo):
    ''' git status

    Parameters:
        <repo>, --repo
            ~parent~
    '''
    g = Git(repo)
    status = g.status()
    print(Text(CLR.m, g.current_branch(), CLR.x))
    if status:
        print(*[f'{s} {f}' for s,f in status])
    else: print(Text(CLR.lg, 'Up to date', CLR.x))


def rebase_ff(base, ontop, *, repo='.'):
    ''' Rebase and then ff merge.  New commits from `ontop` will be applied to `base`.

    Parameters:
        <branch>, --base <branch>  *required* 
            The branch to apply changes to.
        <branch>, --ontop <branch> *required*
            The branch containing new commits.
        --repo <path>
            The repository to work on ('.' by default).
    '''
    self.run('-C', repo, 'rebase', base, ontop)
    self.run('-C', repo, 'switch', base)
    self.run('-C', repo, 'merge', '--ff-only', ontop)

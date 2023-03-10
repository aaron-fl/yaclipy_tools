import sys, os
from pathlib import Path
from .sys_tool import SysTool
from .config import Config


class Git(SysTool):
    cmd = Config.var("An absolute pathname to the git command", 'git')

    @classmethod
    def version(self):
        for line in super().run(self, '--version', stdout=True):
            return line.split(' ')[2]


    def __init__(self, repo='.', **kwargs):
        self.repo = Path(repo)
        super().__init__(**kwargs)


    def __bool__(self):
        return bool(self.name)


    def run(self, *args, **kwargs):
        return super().run('-C', self.repo, *args, **kwargs)


    @property
    def name(self):
        if not hasattr(self, '_name'):
            l = list(self.run('config', '--get', 'remote.origin.url', stdout=True, msg=f'{self.repo}: Origin', or_else=['']))[0]
            if not l:
                l = lines(self.run('rev-parse','--show-toplevel', stdout=True, msg=f'{self.repo}: Name', or_else=['']))[0]
            self._name = os.path.splitext(os.path.basename(l))[0]
        return self._name


    def current_commit(self):
        return list(self.run('rev-parse','HEAD', msg=f'{self.repo}: Current commit', stdout=True))[0]


    def status(self, changes_only=False):
        changes = [x for x in self.run('status', '-z', stdout='raw', msg=f'{self.repo}: Status').decode('utf8').split('\0') if x]
        changes = [(k[:2],k[3:]) for k in changes]
        if changes or changes_only: return changes
        if list(self.run('fetch', '--dry-run', stdout=True, msg=f'{self.repo}: Check pull')):
            return [('  ','Need to pull')]
        if list(self.run('status', '-sb', stdout=True, msg=f'{self.repo}: Check push'))[0].split('[')[-1].startswith('ahead'):
            return [('  ','Need to push')] 
        return []


    def current_branch(self):
        return list(self.run('symbolic-ref', '--short', 'HEAD', stdout=True, msg=f'{self.repo}: Branch'))[0]


    def up_to_date(self):
        return not bool(self.status())


    def list(self, *pattern, invert=False):
        return self.run('ls-files', *pattern, *(['--other'] if invert else []), stdout=True, msg=f'{self.repo}: List')


    def pull_rebase(self, *args):
        self.run('pull', '--rebase', *args)


    def push(self, *args, force=False):
        self.run('push', *(['--force-with-lease'] if force else []), *args)



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


def rebase_ff(base, ontop, *, repo='.', verbose__v=False):
    ''' Rebase and then ff merge.  New commits from `ontop` will be applied to `base`.

    Parameters:
        <branch>, --base <branch>  *required* 
            The branch to apply changes to.
        <branch>, --ontop <branch> *required*
            The branch containing new commits.
        --repo <path>
            The repository to work on ('.' by default).
    '''
    git = Git(repo=repo, verbose=int(verbose__v))
    git.run('rebase', base, ontop)
    git.run('switch', base)
    git.run('merge', '--ff-only', ontop)

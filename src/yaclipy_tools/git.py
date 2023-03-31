import sys, os, asyncio
import yaclipy as CLI
from print_ext import PrettyException
from pathlib import Path
from . import SysTool, OneLine, Watch, Lines


class GitRepoError(PrettyException):
    def __pretty__(self, print, **kwargs):
        print(f"\berr {self.repo}\b  is not a git repository")
    
    @staticmethod
    async def check(tool):
        if not tool.repo: return
        line = await tool.proc.using(OneLine(1))('-C', tool.repo, 'config', '--get', 'remote.origin.url', success=True)
        if not line:
            line = await tool.proc.using(OneLine(1))('-C', tool.repo, 'rev-parse','--show-toplevel')
        return os.path.splitext(os.path.basename(line))[0]



class Git(SysTool):
    cmd = CLI.config_var("An absolute pathname to the git command", 'git')
    used_for = CLI.config_var("Why is this required?", "git is required.")


    @classmethod
    async def get_version(self):
        line = await self.proc.using(OneLine(1))('--version')
        return line.split(' ')[2]


    @classmethod
    def init_once(self, version=0, repo='.', **kwargs):
        self.repo = repo
        self.name = asyncio.create_task(GitRepoError.check(self))
        super().init_once(version, deps=[self.name], **kwargs)
        if self.repo:
            self.proc_verified = self.proc_verified('-C', repo)
    

    def current_commit(self):
        ''' The current commit hash
        '''
        return self.using(OneLine(1))('rev-parse','HEAD')


    async def status(self, *args, changes_only=False):
        ''' A list of changes [(code, file)]

        Parameters:
            changes_only <bool> [False]
                If False, then check if we need to push `: ` or pull `; `
        '''
        changes = await self.using(Lines(end='\0'))('status', '-z', *args)
        changes = [(k[:2],Path(k[3:])) for k in changes if k]
        if changes or changes_only: return changes
        if await self.using(OneLine(1))('fetch', '--dry-run'):
            return [('; ','Need to pull')]
        if await self.using(OneLine(1))('status', '-sb').split('[')[-1].startswith('ahead'):
            return [(': ','Need to push')] 
        return []


    def current_branch(self):
        ''' The name of the current branch.
        '''
        return self.using(OneLine(1))('symbolic-ref', '--short', 'HEAD')


    async def up_to_date(self):
        ''' Check `status()` to see if we are up-to-date.
        '''
        return not bool(await self.status())


    async def list(self, *pattern, invert=False):
        ''' An iterator using `ls-files` to list files based on .gitignore rules.
        '''
        proc = self.using(Watch(1))('ls-files', *pattern, *(['--other'] if invert else []))
        proc.start()
        with proc.mio[1].reader() as read:
            async for line in read.each_line():
                yield Path(line)



async def rebase_ff(base, ontop, *, repo='.', verbose__v=False):
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
    await git('rebase', base, ontop)
    await git('switch', base)
    await git('merge', '--ff-only', ontop)

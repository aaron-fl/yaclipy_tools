import re, os
from functools import partial
from collections import namedtuple
from .sys_tool import SysTool
from .config import Config
from .run import run, CmdNotFound, CmdRunError

exe = Config.var("An absolute pathname to the gpg command", 'gpg')

User = namedtuple('User', ['name','email','me','key'])


class GPG(SysTool):
    re_name = re.compile(r'(.*?)<(.*)>')

    def version(self):
        for line in run(exe(), '--version', stdout=True):
            return line.split(' ')[-1]
    

    def install_help(self, t):
        t('\v\v')
        t('  $ brew install gnupg\v\v')
        t('You should change the pinentry-program so that you can type your password on the command line\v\v')
        t('  $ mkdir -p ~/.gnupg\v')
        t('  $ echo "pinentry-program $(which pinentry-tty)" >> ~/.gnupg/gpg-agent.conf\v')
        return t('  $ gpgconf --kill gpg-agent\v')


    def import_key(self, fname, verbose=None):
        #if verbose==None: verbose = self.verbose
        runv = partial(run, verbose=verbose or 0)
        key_id = ''
        for line in runv('gpg','--with-colons','--import-options','show-only','--keyid-format','long','--import',fname, stdout=True, msg="Finding keys", or_else=[]):
            if line.startswith('pub'):
                key_id = line.split(':')[4]
            if line.startswith('uid'):
                line = line.split(':')
                usr_hash = line[7]
                usr_name = line[9]
        if key_id == '': return None
        if runv('gpg','--list-keys', key_id, or_else=True):
            runv('gpg','--import',fname, msg=f'Importing key for user: \b1 {usr_name}')
        me = not runv('gpg','--list-secret-keys', key_id, or_else=True)
        name, email = GPG.re_name.match(usr_name).groups()
        return User(name=name.strip(), email=email, me=me, key=key_id)


    def export_key(self, email, fname, verbose=None):
        #if verbose==None: verbose = self.verbose
        run('gpg','--yes','--armor','--output',fname,'--export',email, msg="Exporting key", verbose=verbose or 0)
    
 
    def list_users(self, verbose=None):
        #if verbose==None: verbose = self.verbose
        for line in run('gpg -K --with-colons', stdout=True, msg="List Users", verbose=verbose or 0):
            if line.startswith('uid'):
                line = line.split(':')
                name, email = GPG.re_name.match(line[9]).groups()
                yield User(name=name.strip(), email=email, me=True, key=line[7])
    

    def genkey(self, verbose=None):
        run('gpg --full-generate-key', verbose=verbose or 0)


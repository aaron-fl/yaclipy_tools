import re, os
from collections import namedtuple
from .sys_tool import SysTool
from .config import Config
from .run import run, CmdNotFound, CmdRunError

User = namedtuple('User', ['name','email','me','key'])

NAME_RE = re.compile(r'(.*?)<(.*)>')


class GPG(SysTool):
    
    cmd = Config.var("An absolute pathname to the gpg command", 'gpg')

    @classmethod
    def version(self):
        for line in self.__call__(self, '--version', stdout=True):
            return line.split(' ')[-1]
    
    
    @classmethod
    def install_help(self, t):
        t('\v\v')
        t('  $ brew install gnupg\v\v')
        t('You should change the pinentry-program so that you can type your password on the command line\v\v')
        t('  $ mkdir -p ~/.gnupg\v')
        t('  $ echo "pinentry-program $(which pinentry-tty)" >> ~/.gnupg/gpg-agent.conf\v')
        return t('  $ gpgconf --kill gpg-agent\v')


    def import_key(self, fname):
        key_id = ''
        for line in self('--with-colons','--import-options','show-only','--keyid-format','long','--import',fname, stdout=True, msg="Finding keys", or_else=[]):
            if line.startswith('pub'):
                key_id = line.split(':')[4]
            if line.startswith('uid'):
                line = line.split(':')
                usr_hash = line[7]
                usr_name = line[9]
        if key_id == '': return None
        if self('--list-keys', key_id, or_else=True):
            self('--import',fname, msg=f'Importing key for user: \b1 {usr_name}')
        me = not self('--list-secret-keys', key_id, or_else=True)
        name, email = NAME_RE.match(usr_name).groups()
        return User(name=name.strip(), email=email, me=me, key=key_id)


    def export_key(self, email, fname):
        self('--yes','--armor','--output',fname,'--export',email, msg="Exporting key")
    
 
    def list_users(self):
        for line in self('-K','--with-colons', stdout=True, msg="List Users"):
            if line.startswith('uid'):
                line = line.split(':')
                name, email = NAME_RE.match(line[9]).groups()
                yield User(name=name.strip(), email=email, me=True, key=line[7])
    

    def genkey(self):
        self('--full-generate-key')

import re, os
import yaclipy as CLI
from collections import namedtuple
from . import SysTool, OneLine, Lines

User = namedtuple('User', ['name','email','me','key'])


class GPG(SysTool):
    cmd = CLI.config_var("An absolute pathname to the gpg command", 'gpg')
    used_for = CLI.config_var("Why is this required?", "gpg is required.")


    @classmethod
    async def get_version(self):
        line = await self.proc.using(OneLine(1))('--version')
        return line.split(' ')[-1]

    
    @classmethod
    def init_once(self, *args, **kwargs):
        self.NAME_RE = re.compile(r'(.*?)<(.*)>')
        super().init_once(*args, **kwargs)


    @classmethod
    def install_help_macos(self, print):
        print("Install using brew:")
        print("  $ brew install gnupg")


    @classmethod
    def install_help_generic(self, print):
        print("https://gnupg.org/download/")
        print('You can change the pinentry-program so that you can type your password on the command line:')
        print(' $ mkdir -p ~/.gnupg')
        print(' $ echo "pinentry-program $(which pinentry-tty)" >> ~/.gnupg/gpg-agent.conf')
        print(' $ gpgconf --kill gpg-agent')


    async def import_key(self, fname):
        key_id = ''
        for line in await self.using(Lines(1))('--with-colons', '--import-options', 'show-only', '--keyid-format', 'long', '--import', fname, or_else=[]):
            if line.startswith('pub'):
                key_id = line.split(':')[4]
            if line.startswith('uid'):
                line = line.split(':')
                usr_hash = line[7]
                usr_name = line[9]
        if key_id == '': return
        if await self('--list-keys', key_id, or_else=True):
            await self('--import', fname)
        me = not await self('--list-secret-keys', key_id, or_else=True)
        name, email = self.NAME_RE.match(usr_name).groups()
        return User(name=name.strip(), email=email, me=me, key=key_id)


    def export_key(self, email, fname):
        return self('--yes', '--armor', '--output', fname, '--export', email)
    
 
    async def each_user(self):
        for line in await self.using(Lines(1))('-K', '--with-colons'):
            if not line.startswith('uid'): continue
            line = line.split(':')
            name, email = self.NAME_RE.match(line[9]).groups()
            yield User(name=name.strip(), email=email, me=True, key=line[7])
    

    def genkey(self):
        return self('--full-generate-key')

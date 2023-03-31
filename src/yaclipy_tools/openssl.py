import os, re
import yaclipy as CLI
from print_ext import PrettyException
from . import OneLine, SysTool, Echo


class CertificateExists(PrettyException): pass


class OpenSSL(SysTool):
    cmd = CLI.config_var("An absolute pathname to the openssl command", 'openssl')
    used_for = CLI.config_var("Why is this required?", "openssl is required.")

    @classmethod
    async def get_version(self):
        line = await self.proc.using(OneLine(1))('version', '-v')
        return line.split(' ')[1]


    @classmethod
    def install_help_macos(self, print):
        print("Install using brew:")
        print("  $ brew install openssl")


    @classmethod
    def install_help_generic(self, print):
        print("https://www.openssl.org/source/")


    async def cert_inspect(self, prefix, mode='-subject'):
        line = await self.using(OneLine(1))('x509', '-in', str(prefix)+'.pem', mode, '-noout')
        return {a[0]:a[1] for a in [arg.split(' = ',1) for arg in line[len(mode):].split(', ')]}


    async def cert(self, *, prefix, cn, ca, san=[], client=False, force=False, askpass=False, days=365):
        prefix = str(prefix)
        if not force and os.path.exists(prefix+'.pem'):
            self.cert_show(prefix, '-text')
            raise CertificateExists(msg=f"Certificate exists: \b1 {prefix+'.pem'}\b \nUse `--force` to overwrite")
        os.makedirs(os.path.split(prefix)[0], exist_ok=True)
        subj=f'/O=yaclipy-tools/CN={cn}'
        #subjcn = ''.join([f'/CN={cn}' for cn in cn if '*' not in cn])
        sancn = ','.join([f'IP:{x}' if re.search(r'^[0-9.:]+$',x) else f'DNS:{x}' for x in san])

        cmd = ['req', '-x509', '-sha256', '-out', prefix+'.pem', '-newkey', 'rsa:2048', '-keyout', prefix+'-key.pem', '-days', str(days), '-subj', subj]
        if not askpass:
            cmd += ['-noenc']
        if ca:
            cmd += ['-CA', ca+'.pem']
            cmd += ['-CAkey', ca+'-key.pem']
            cmd += ['-addext', 'basicConstraints=critical,CA:FALSE']
            cmd += ['-addext', 'subjectKeyIdentifier=none']
            if client:
                cmd += ['-addext', 'extendedKeyUsage=clientAuth']
            else:
                #Key Usage: critical, Digital Signature, Key Encipherment
                cmd += ['-addext', 'extendedKeyUsage=serverAuth']
        else:
            cmd += ['-addext', 'basicConstraints=critical,CA:TRUE']
            cmd += ['-addext', 'keyUsage=critical,keyCertSign']
            cmd += ['-addext', 'subjectKeyIdentifier=hash']
            cmd += ['-addext', 'authorityKeyIdentifier=none']
        if sancn:
            cmd += ['-addext', f'subjectAltName={sancn}']
        
        await self(*cmd)
        return await self.cert_inspect(prefix)


    def rsa(self, *, path):
        self('genrsa', '-traditional', '-out', path)


    async def rand(self, *, path=None, bytes=32):
        if path:
            await self('rand', '-hex', '-out', path, bytes)
        else:
            return await self.using(OneLine(1))('rand','-hex', bytes)
        

    async def hash(self, path):
        line = await self.using(OneLine(1))('dgst', '-sha256', '-hex', '-r', path, or_else=None)
        return '' if line == None else line.split(' ',1)[0]

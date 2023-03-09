import os, re
from print_ext import PrettyException
from .sys_tool import SysTool
from .config import Config


class CertificateExists(PrettyException): pass


class OpenSSL(SysTool):

    cmd = Config.var("An absolute pathname to the openssl command", 'openssl')

    @classmethod
    def version(self):
        for line in self.run(self, 'version', '-v', stdout=True):
            return line.split(' ')[1]

    @classmethod
    def install_help(self, t):
        return t("\v\v $ brew install openssl")

    
    def cert_inspect(self, prefix, mode='-subject'):
        for line in self.run('x509', '-in', str(prefix)+'.pem', mode, '-noout', stdout=True, msg="Inspect Certificate"):
            return {a[0]:a[1] for a in [arg.split(' = ',1) for arg in line[len(mode):].split(', ')]}


    def cert(self, *, prefix, cn, ca, san=[], client=False, force=False, askpass=False, days=365):
        prefix = str(prefix)
        if not force and os.path.exists(prefix+'.pem'):
            self.cert_show(prefix, '-text')
            raise CertificateExists(msg = (f"Certificate exists: \b1 {prefix+'.pem'}", "\vUse `--force` to overwrite"))
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
        
        self.run(*cmd, msg=f"Openssl Certificate: {prefix!r}  ca:{ca}  cn:{cn}  san:{san}")
        return self.cert_inspect(prefix)


    def rsa(self, *, path, format):
        self.run('genrsa', '-traditional', '-out', path)


    def rand(self, *, fname=None, bytes=32):
        if fname:
            self.run('rand', '-hex', '-out', str(fname), str(bytes))
        else:
            for line in self.run('rand','-hex', bytes, stdout=True):
                return line.rstrip()
        

    def hash(self, fname):
        for line in self.run('dgst', '-sha256', '-hex', '-r', fname, stdout=True, msg=f"Calculate file hash of '{fname}'", or_else=['']):
            return line.split(' ',1)[0]

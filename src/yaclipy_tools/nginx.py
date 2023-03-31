import sys, os, logging
import yaclipy as CLI
from print_ext import Printer
from pathlib import Path
from . import SysTool, OneLine
from .curl import Curl


log = logging.getLogger('Nginx-Tool')


class Nginx(SysTool):
    cmd = CLI.config_var("An absolute pathname to the nginx command", 'nginx')
    used_for = CLI.config_var("Why is this required?", "nginx is required.")
    cert = CLI.config_var("The nginx certificate to use", 'local/dev.localhost', lambda v: Path(v))

    @classmethod
    async def get_version(self):
        line = await self.proc.using(OneLine(2))('-v')
        return line.rsplit('/',1)[1]


    @classmethod
    def init_once(self, *args, **kwargs):
        curl_args = {k:v for k,v in kwargs.items() if k in ['context']}
        self.curl = Curl('7', **curl_args)
        super().init_once(*args, deps=[self.curl.version], **kwargs)


    @classmethod
    def install_help_macos(self, print):
        print("Install using brew:")
        print("  $ brew install nginx")


    @classmethod
    def install_help_generic(self, print):
        print("https://nginx.org/download")


    def __init__(self, **kwargs):
        self.cfg = dict(workers = 1, domains={}, prefix=Path('local/nginx'), port=80, cert=self.cert())
        self.config()


    def __getitem__(self, k):
        return self.cfg[k]


    def config(self, **kwargs):
        self.cfg.update(kwargs)
        cfg = [
            f"worker_processes {self['workers']}",
            f"pid {self['prefix']/'nginx.pid'}",
            ('events', [
                'worker_connections 1024',
                'accept_mutex ' + ('on' if self['workers'] > 1 else 'off'),
            ]),
            ('http', [f"{x}_temp_path {self['prefix']}" for x in ['client_body', 'proxy', 'fastcgi','uwsgi','scgi']] + 
            [f'proxy_set_header {x} {y}' for x,y in {'X-Forwarded-For':'$proxy_add_x_forwarded_for', 'X-Forwarded-Proto':'$scheme', 'Host':'$http_host'}.items()] + [
                "log_format dev '[$status] $upstream_response_time $http_host $request'",
                f"access_log {self['prefix']/'nginx.log dev'}",
                'sendfile on',
                'proxy_redirect off',
                'keepalive_timeout 5',
                'client_max_body_size 10M',
                'include mime.types',
                'server_names_hash_bucket_size 64',
            ]),
        ]
        if self['cert'].is_file():
            cfg[-1][1].append(f"ssl_certificate {self['cert']}.pem")
            cfg[-1][1].append(f"ssl_certificate_key {self['cert']}-key.pem")
            if self['port'] == 80:
                cfg[-1][1].append(('server', ['listen 80', 'server_name _', 'return 301 https://$host$request_uri']))
        for domain, locs in self['domains'].items():
            if domain: domain += '.'
            srv = [
                f"listen {443 if self['cert'] and self['port'] == 80 else self['port']}" + (' ssl' if self['cert'] else ''),
                f'server_name {domain}dev.localhost',
               
            ]
            for x in locs:
                if isinstance(x, tuple):
                    d = f'proxy_pass {x[1]}' if x[1].startswith('http') else x[1]
                    srv.append((f'location {x[0]}', [d]))
                else:
                    srv.append(x)
            if '/' not in [x[0] for x in locs if isinstance(x, tuple)]:
                srv.append(('location /', ['try_files $uri $uri.html $uri/ /index.html']))
            cfg[-1][1].append(('server', srv))
        self.cfg_tree = cfg
        return self
    

    async def start(self):
        self['prefix'].mkdir(exist_ok=True)
        mime = self['prefix']/'mime.types'
        if not mime.is_file():
            await self.curl.download('https://raw.githubusercontent.com/nginx/nginx/master/conf/mime.types', mime)
        with (self['prefix']/'nginx.conf').open('w') as f:
            def clean(x, depth=0):
                for l in x:
                    if isinstance(l, tuple):
                        yield ' '*4*depth + l[0] + ' {\n'
                        yield from clean(l[1], depth+1)
                        yield ' '*4*depth + '}\n'
                    else:
                        yield ' '*4*depth + l + ';\n'
            f.write(''.join(clean(self.cfg_tree)))
        if not self['cert'].is_file():
            Printer(f"No certificate file {self['cert']}: https disabled.", "warn")
        await self('-c', self['prefix']/'nginx.conf', '-p', os.path.abspath('.'), '-e', self['prefix']/'error.log')


    async def stop(self):
        await self('-s', 'stop', '-c', self['prefix']/'nginx.conf', '-p', os.path.abspath('.'))

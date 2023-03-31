import logging, re
import yaclipy as CLI
from print_ext import Table, Printer, Line
from collections import namedtuple
from . import SysTool
from subprocess import Popen, PIPE, DEVNULL

log = logging.getLogger('Grep-Tool')


grep_groups = CLI.config_var(''' A dictionary of project locations that will be grepped with the grep command.

    {
        'Python Files': [
            (None, 'file1.py', 'file2.py'),
            ('py', 'src/pyutil', '*/__pycache__/*', */.python/*'),
        ],
        'State Files': [
            ('dart,py', 'src/state', '*/__pycache__/*', '*/.dist/*'),
            ('*', '*/docs/*', '*. '*/.dist/*'),
        ],
    }
''', {'':[('*', '.', '*/__pycache__/*', '*/node_modules/*', 'local/*')]})


FileMatch = namedtuple('FileMatch', ('fname','lno','match'))
def _from_str(s):
    fn, lno, match = s.split(':',2)
    return FileMatch(fname=fn, lno=lno, match=match)
FileMatch.from_str = _from_str



class GroupMatch(dict):
    def __init__(self, groups, pattern=None, case=False):
        self.re = re.compile(pattern, flags=0 if case else re.IGNORECASE) if pattern else None
        super().__init__({k:[FileMatch.from_str(line) for line in v.splitlines()] for k,v in groups.items()})


    def __pretty__(self, print, **kwargs):
        if not(self):
            print('\bwarn No matches')
            return
        for title, files in self.items():
            tbl = Table(0,1, tmpl='')
            tbl.cell('c0', just='>')
            fn = ''
            for f in files:
                if self.re:
                    i = 0
                    line = Line()
                    for m in self.re.finditer(f.match):
                        s, e = m.span()
                        if s != i:
                            line.insert(-1,f.match[i:s])
                        if s != e:
                            line.insert(-1,f.match[s:e],style='err')
                        i = e
                    if i < len(f.match):
                        line.insert(-1, f.match[i:])
                else:
                    line = Line(f.match)
                tbl(f"\b{'1' if fn!=f.fname else 'w.;'} {f.fname}\bw.; :\b2 {f.lno} \t", line,'\t')
                fn = f.fname
            if tbl:
                print.hr(title, style='em')
                print(tbl)



class Grep(SysTool):
    cmd = CLI.config_var("An absolute pathname to the grep command", 'grep')
    needed_because = CLI.config_var("Why is this required?", "grep is required.")


    @classmethod
    async def get_version(self):
        line = await self.proc('--version').one()
        return line.rsplit(' ',1)[1].split('-')[0]
    

    def files_search(self, files, pattern, *args):
        if not files: return ''
        cmd = ['--color=never'] + list(args) + [pattern] + files
        return self(*cmd)


    def group_search(self, groups, pattern, *args):
        def _group_cmds():
            base = [self.cmd()] + list(args)
            for mod, locs in groups.items():
                for loc in locs:
                    if loc[0]:
                        exclude = [f'--exclude={e}' for e in loc[2:]]
                        include = [] if loc[0] == '*' else [f'--include=*.{e.strip()}' for e in loc[0].split(',') if e.strip()]
                        cmd = base + include + exclude + ['-r', pattern, loc[1]]
                    else:
                        cmd = base + [pattern] + list(loc[1:]) + ['/dev/null']
                    log.debug(' '.join(cmd))
                    yield mod, cmd
        g = {}
        for m, p in [(m, Popen(cmd, stderr=DEVNULL, stdout=PIPE)) for m, cmd in _group_cmds()]:
            g[m] = p.communicate()[0].decode('utf8') or ''#[FileMatch.from_str(line) for line in  .splitlines()]
        return g




async def grep(pattern, /, *, case__c=False) -> GroupMatch:
    ''' Grep all relevant files (and filenames) in the project for regex <pattern>

    Parameters:
        <pattern>
            A regex pattern to search for
        --case, -c
            Case sensitive search
    '''
    args = ['-n', '--color=never']
    if not case__c: args += ['-i']
    data = Grep().group_search(grep_groups(), pattern, *args)
    return GroupMatch(data, pattern, case__c)

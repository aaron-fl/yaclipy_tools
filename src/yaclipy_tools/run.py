from print_ext import print, PrettyException, Text, HR
import asyncio, time
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired

class CmdRunError(PrettyException):
    def pretty(self, verbose=9, **kwargs):
        raw = type('raw',(object,), {'__str__':lambda self: self.m, '__init__': lambda self,x: setattr(self,'m',x)})
        f = Text()
        if self.stdout: f(HR('Captured stdout call', style='1'),'\v\v')
        for s in self.stdout:
            f(raw(s), '\v')
        if self.stderr: f(HR('Captured stderr call', style='1'),'\v\v')
        for s in self.stderr:
            f(raw(s),'\v')
        f('\v',HR(self.__class__.__name__, style='err'), '\v\v')
        if self.msg: f(*self.msg,'\v\v')
        f(' $ ', raw(self.cmd), '\v')
        f(' -> ')
        f('Command not found.' if self.returncode == None else self.returncode, style='err')
        return f('\v')


class CmdNotFound(CmdRunError): pass



def run_parallel(cmd_f, *services, msg=None):
    cmds = cmd_f if services==None else [(svc, cmd_f(svc)) for svc in list(services)]
    if not cmds: return
    if msg: print(msg)
    #print('\n'.join(f"{svc} : {' '.join(cmd)}" for svc, cmd in cmds))
    failed = []
    outputs = {}
    for svc, cmd, proc in [(s, cmd, Popen(cmd, stdout=PIPE, stderr=PIPE)) for (s, cmd) in cmds]:
        std_out, std_err = proc.communicate()
        if proc.returncode:
            print(f"Command failed for {svc}: ", ' '.join(cmd))
            sys.stdout.write(std_err.decode('utf8'))


def run(*args, msg=None, verbose=0, stdin=None, stdout=False, stderr=False, success=[0], shell=False, raw=False, **kwargs):
    ''' Run a command.
    
    Parametes:
        <cmd>
            A string or array of command arguments.
            Strings are split by spaces if shell=False, otherwise given as-is
        verbose <int>
            How much output do you want to see?
              0: Silent
              1: Print executing command with spinner
              2: Show command line
              3: Print command and its output
        stdin <None | str>
            The string data to feed to the process
        stdout <bool>
            Capture stdout True/False
        stderr <bool> | None
            Capture stderr? or copy stdout (None)
        success int | [int] | True
            if success is an integer or array of integers then throw an exception
            if the returncode does not match
    '''
    if not isinstance(msg, tuple): msg = None if msg==None else tuple(msg)
    cmd = list(map(str, args[0] if len(args) == 1 else args))
    cmd_str = cmd if isinstance(cmd, str) else ' '.join((f'"{c}"' if ' ' in c else c) for c in cmd)
    if not shell and isinstance(cmd, str): cmd = cmd.split(' ')
    # Show some stuff
    if verbose >= 2:
        print.flex('  $ \t', cmd_str)
    if verbose >= 1 and msg:
        print(*msg)
    # Try to Popen
    try:
        proc = Popen(cmd,
            stdout = None if not stdout and verbose >= 3 else PIPE,
            stderr = None if not stderr and verbose >= 3 else PIPE,
            stdin = PIPE if stdin else None,
            shell=shell, **{k:v for k,v in kwargs.items() if k not in ['or_else']})
    except Exception as e:
        raise CmdNotFound(cmd=cmd_str, stderr=[f'{e}'], stdout=[], msg=msg, returncode=None)
    # Wait for output
    spin = print.progress()
    t0 = time.time()
    timeout = 1.0 if verbose in [1,2] else None
    while True:
        try:
            out = proc.communicate(timeout=timeout, input=stdin)
            sout = [out[0]] if stdout=='raw' else (out[0] or bytes()).decode('utf8').splitlines()
            serr = [out[1]] if stderr=='raw' else (out[1] or bytes()).decode('utf8').splitlines()
            break
        except TimeoutExpiredTimeoutExpired:
            timeout = 0.2
            spin(f"{time.time() - t0:.1f}")
    if verbose >= 1: spin(f' -> {proc.returncode}',done=True)
    if success==True: success = [proc.returncode]
    if isinstance(success, int): success = [success]
    if proc.returncode in success:
        if not stdout and not stderr: return proc.returncode
        if stdout == 'raw': return sout[0]
        if stderr == 'raw': return sout[1]
        return iter((sout if stdout else []) + (serr if stderr else []))
    if 'or_else' in kwargs:
        return kwargs['or_else']
    raise CmdRunError(cmd=cmd_str, stdout=sout, stderr=serr, msg=msg, returncode=proc.returncode)

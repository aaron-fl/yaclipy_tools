import asyncio, shlex, functools
from subprocess import PIPE, DEVNULL
from print_ext import PrettyException
from .plugin import Plugin, NO_RESULT
from ..mio import MioBuffer



class ReturncodeError(PrettyException):
    def __pretty__(self, print, **kwargs):
        print(f" $ ", shlex.join(self.proc.cmd))
        print(f"Command failed with returncode: \berr {self.proc.returncode}")


class ManyError(PrettyException):
    def __pretty__(self, print, **kwargs):
        print(f"\berr Multiple Exceptions were raised")
        for e in self.exceptions:
            print.hr(str(e))
            print.pretty(e)
        


class MetaProcTask(type):
    def __call__(self, *args, **kwargs):
        kw = dict(self.partial)
        kw.update(kwargs)
        cmd = kw.pop('_cmd')
        return super().__call__(*cmd, *args, **kw)


    def using(self, *plugins, **partial):
        partial.setdefault('_cmd', tuple(self.partial['_cmd']))
        d = {
            'plugins': self.plugins + [x if isinstance(x, Plugin) else x() for x in plugins],
            'partial': partial,
        }
        for m in d['plugins']:
            if not isinstance(m, Plugin): raise ValueError(f"Mixins must be subclasses of Plugin, not {type(m)} {m}")
            for name in dir(m):
                try:
                    fn = getattr(m.__class__,name)
                    fn.is_proc_task_method
                except: continue
                d[name] = getattr(m.__class__,name)
        name = 'ProcTask' + ''.join(set(m.__class__.__name__ for m in d['plugins']))
        return type(name, (ProcTask, ), d)

    



class ProcTask(asyncio.SubprocessProtocol, metaclass=MetaProcTask):
    plugins = []
    partial = {'_cmd':tuple()}
    
    def __init__(self, *args, name=None, success=[0], or_else=NO_RESULT, context=None, **kwargs):
        self.name = name
        self.or_else = or_else
        self.success = success
        self.context = context
        self.cmd = tuple(shlex.split(str(args[0])) if len(args) == 1 else list(map(str, args)))
        self.task = None


    def __call__(self, *args, **kwargs):
        return self.__class__(*self.cmd, *args, _cmd=tuple(), **self._partial(kwargs))


    def _partial(self, kwargs):
        return dict(
            name = kwargs.get('name', None) if self.name == None else str(self) + kwargs.get('name', ''),
            success = kwargs.get('success', self.success),
            context = kwargs.get('context', self.context),
            or_else = kwargs.get('or_else', self.or_else),
        )


    def __str__(self):
        if self.name == None:
            return self.task.get_name() if self.task else ''
        return str(self.name)


    def _using(self, *args, **kwargs):
        partial = self._partial(kwargs)
        partial['_cmd'] = tuple(self.cmd)
        return ProcTask.using(*self.plugins, *args, **partial)


    def start(self):
        ''' Just start the process and return a running asyncio.Task
        '''
        if self.task: return self.task
        # Create the main task
        loop = asyncio.get_running_loop()
        def _create():
            return loop.create_task(self._coro(), name=self.name and str(self.name))
        self._connection_lost = loop.create_future()
        self._pipe_exc = {}
        self._plugins = [m(self) for m in self.plugins]
        # Choose the best buffer for everyone to share
        def _select_buffer(fd, pbuf, m):
            buf = m.fd_buffer(fd)
            if buf == None: return pbuf
            if pbuf == None: return buf
            return pbuf if buf < pbuf else buf
        # Buffers for stdin, stdout, stderr, stdout+stderr
        self.mio = [
            None,
            functools.reduce(functools.partial(_select_buffer, 1), self._plugins, None),
            functools.reduce(functools.partial(_select_buffer, 2), self._plugins, None),
            functools.reduce(functools.partial(_select_buffer, 3), self._plugins, None),
        ]
        # Which buffers are we in charge of creating / maintaining?
        self._auto_fd = set()
        for i, buf in enumerate(self.mio):
            if buf != True: continue
            self.mio[i] = MioBuffer()
            self._auto_fd.add(i)
        # Create the task, possibly in a context
        self.task = _create() if self.context == None else self.context.run(_create)
        return self.task 


    async def _coro(self):
        ''' Start the task, if it isn't already running, and wait for it to complete`
        '''
        loop = asyncio.get_running_loop()
        try:
            await asyncio.gather(*[m.prepare() for m in self._plugins])
            stdout = DEVNULL if self.mio[1]==None and self.mio[3]==None else PIPE
            stderr = DEVNULL if self.mio[2]==None and self.mio[3]==None else PIPE
            await loop.subprocess_exec(lambda: self, *self.cmd, stdin=PIPE, stdout=stdout, stderr=stderr)
            await asyncio.gather(*[m.run() for m in self._plugins])
            exc = await self._connection_lost
            # The process has terminated.  Did we collect any exceptions along the way?
            self.exceptions = [v for v in (exc, *self._pipe_exc.values()) if v]
        finally:
            aws = [self.mio[fd].close() for fd in self._auto_fd]
            aws += [m.cleanup() for m in self._plugins]
            await asyncio.gather(*aws)
        # Did we create exceptions
        rval = self.returncode
        if self.success!=True and self.returncode not in self.success:
            if self.or_else == NO_RESULT:
                self.exceptions.append(ReturncodeError(proc=self))
            else:
                rval = self.or_else
        if len(self.exceptions) == 1: raise self.exceptions[0]
        elif len(self.exceptions) > 1: raise ManyError(exceptions=self.exceptions) # 3.11 ExceptionGroup
        # Figure out the return value
        v = functools.reduce(lambda a,m: (*a, v) if (v:=m.result()) != NO_RESULT else a, self._plugins, tuple())
        if not v: return rval
        return v[0] if len(v) == 1 else v


    def kill(self):
        if not self.task or self.done(): return
        self._transport.kill()
        return self

    
    def send_signal(self, signal):
        if not self.task or self.done(): return
        self._transport.send_signal(signal)
        return self

    
    def __pretty__(self, print, **kwargs):
        print("OBJ: ", self.__class__.__name__, '\b1$', str(self))
        print(f" $ ", shlex.join(self.cmd))
        print.pretty(self.__class__)


    @classmethod
    def __pretty__(self, print, **kwargs):
        print('CLS: ', self.__name__)
        print.pretty({'partial':self.partial, 'plugins':self.plugins})


    # Task Methods

    def __getattr__(self, attr):
        if attr == 'using':
            return self._using if isinstance(self, ProcTask) else getattr(self.__class__, 'using')
        elif hasattr(self.task, attr):
            return getattr(self.task, attr)
        return super().__getattribute__(attr)


    def result(self):
        return self.task.result()


    def __await__(self):
        self.start()
        yield from self.task.__await__()
        return self.task.result()


    def done(self):
        return self._connection_lost.done()


    def cancel(self):
        if not self.task or self.done(): return
        self._transport.terminate()
        return self


    # SubprocessProtocol Methods

    def connection_made(self, transport):
        self._transport = transport
        self.pid = transport.get_pid()
        for m in self._plugins: m.connected(transport)


    def pipe_data_received(self, fd, data):
        if 3 in self._auto_fd: self.mio[3].write(data)
        if fd in self._auto_fd: self.mio[fd].write(data)
        for m in self._plugins: m.fd_data(fd, data)


    def pipe_connection_lost(self, fd, exc):
        self._pipe_exc[fd] = exc
        # Close it
        if fd in self._auto_fd: self.mio[fd].write(None)
        for m in self._plugins: m.fd_closed(fd)
        # Close 3
        if {1,2} - self._pipe_exc.keys(): return # Haven't closed 1 and 2 yet
        if 3 in self._auto_fd: self.mio[3].write(None) 
        for m in self._plugins: m.fd_closed(3)


    def process_exited(self):
        self.returncode = self._transport.get_returncode()      
        

    def connection_lost(self, exc):
        self._connection_lost.set_result(exc)

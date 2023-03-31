

NO_RESULT = type('NO_RESULT', tuple(), {'__repr__': lambda _: 'NO_RESULT'})()


class Plugin():
    @classmethod
    def export(self, fn):
        fn.is_proc_task_method = True
        return fn


    def __init__(self, *args, _proc=None, **kwargs):
        ''' If we are create with a `proc` kw argument then we are running a command ''' 
        if _proc:
            self.proc = _proc
            self.start(*args, **kwargs)
        else:
            self.__args = (args, kwargs)


    def __call__(self, proc):
        return self.__class__(*self.__args[0], _proc=proc, **self.__args[1])


    def start(self):
        ''' Called in before the proc Task has been created '''


    def connected(self, transport):
        ''' Called when we have a transport '''

    
    async def prepare(self):
        ''' Called before the process is created '''


    async def run(self):
        ''' Called after the process has been created '''


    async def cleanup(self):
        ''' Called after the process has exited (error or not '''


    def fd_data(self, fd, data):
        ''' Data has come in on fd 1 or 2'''


    def fd_closed(self, fd):
        ''' Fd 1 2 or 3 has closed '''


    def fd_buffer(self, fd):
        ''' Return a MioBase object, True, or None.
        
        * MioBase buffer: We are using this buffer, and other plugins can use it too.
          This plugin is in charge of writing to it and closing it.
        * True: We need a buffer, but any buffer will do.  ProcTask will manage it.
        * None: We don't need this `fd`.
        '''


    def result(self):
        ''' Return a value as the primary result().  If multiple pluginss return a value then a tuple is returned. '''
        return NO_RESULT

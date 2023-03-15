#!/usr/bin/env python
import os, sys
from subprocess import call
from os.path import join, abspath, split, exists

VENV_DIR='.python' # This can be moved if needed
REQ = 'pyutil/requirements.txt' # This can be moved/renamed

def abort(*reason):
    print('\n'+'!'*75,'\nERROR:', *reason)
    print('Look above for the specific error.','\n'+'!'*75,'\n')
    import shutil
    shutil.rmtree(VENV_DIR, ignore_errors=True)
    sys.exit(1)

os.chdir(split(abspath(__file__))[0]) # Make the cwd the same as this file
if sys.prefix == sys.base_prefix: # Not in the virtual env
    new = not exists(VENV_DIR)
    if new and call(['python3', '-m','venv',VENV_DIR]):
        abort("Couldn't create python3 virtual environment at", VENV_DIR)
    os.environ['PATH'] = join(VENV_DIR,'bin') + os.pathsep + os.environ['PATH']
    if new and call(['python', '-m', 'pip', 'install', 'yaclipy']):
        abort("Couldn't install yaclipy into the virtual environment")
    os.execvp('python', ['python', './cli.py'] + sys.argv[1:])

# Now we are running in the virtual environment.
# Install REQ requirements and run the main command.
import yaclipy as CLI
from print_ext import print, PrettyException

try:
    #CLI.ensure_requirements(req=REQ, venv=VENV_DIR)
    from pyutil.main import main
    CLI.Command(main)(sys.argv[1:]).run()
except PrettyException as e:
    print.pretty(e, pad=1)

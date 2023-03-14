import logging, time
from print_ext import print
from .some_tool import SomeTool
import yaclipy as CLI
from yaclipy_tools.config import Config

log = logging.getLogger('clipy-main')



def run():
    ''' Run the project
    '''
    tool = SomeTool()
    log.info('Running...')
    log.warn('Uh-oh')
    log.debug('Fixing stuff')
    tool.do_something()



def build():
    ''' Build the project
    '''
    log.info('Building...')
    p = print.progress(steps=42)
    for f in range(42):
        p('Process \b2$', f, '\b$ ...')
        time.sleep(0.1)
    p('Done!', done=True)


    
def deploy():
    ''' Deploy the project
    '''
    log.info('Deploying...')


def config():
    ''' Show the current configuration
    '''
    return Config



@CLI.sub_cmds(run, build, deploy, config)
def main(*, verbose__v=False, quiet__q=False, target__t=''):
    ''' This is the sole entrypoint for this project.
    
    Parameters:
        --verbose, -v
            Increase the logging level by one notch
        --quiet, -q
            Decrease the logging level by one notch
    '''
    level = max(0, min(50, 20 - 10*(int(verbose__v) - int(quiet__q))))
    logging.basicConfig(style='{', format='{levelname:>7} {name:>10} {lineno:<3} | {message}', level=level)
    import config
    Config.set_target(target__t or 'dev')

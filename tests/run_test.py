from yaclipy_tools.run import run, CmdRunError, CmdNotFound
from .testutil import printer


def test_run_exception():
    try:
        run('tests/echo.py', '3', 'std\nout', 'stderr\n')
    except CmdRunError as e:
        o, p = printer(ascii=True)
        p.pretty(e)
        assert(o.getvalue() == '\n-[ Captured stdout call ]-\n\nstd\nout\n\n-[ Captured stderr call ]-\n\nstderr\n\n-[ CmdRunError ]-\n\n $ tests/echo.py 3 std\\x0aout stderr\\x0a\n -> 3\n\n')


def test_run_noexception_stdout():
    l = list(run('tests/echo.py', '3', 'std\nout', 'stderr\n', stdout=True, success=3))
    assert(l == ['std','out'])

def test_run_noexception_stdout_stderr():
    l = list(run('tests/echo.py', '3', 'std\nout', 'stderr\n', stdout=True, stderr=True, success=3))
    assert(l == ['std','out','stderr',''])


def test_run_noexception_nothing():
    l = run('tests/echo.py', '3', 'std\nout', 'stderr\n', success=3)
    assert(l == 3)


def test_run_notfound():
    try:
        run('tests/ecfsdho.py', '3', 'stdout', 'stderr', success=3)
    except CmdNotFound as e:
        o, p = printer(ascii=True)
        p.pretty(e)
        assert(o.getvalue() == "\n-[ Captured stderr call ]-\n\n[Errno 2] No such file or directory: 'tests/ecfsdho.py'\n\n-[ CmdNotFound ]-\n\n $ tests/ecfsdho.py 3 stdout stderr\n -> Command not found.\n\n")



if __name__=='__main__':
    for line in run('echo the quick brown fr\nox jumped over the lazy dog', verbose=2, msg=("Hello", ' world')):
        print(f'<<{line}>>')
    print("DONE")

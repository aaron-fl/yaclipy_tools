import io
from print_ext import Printer

def printer(**kwargs):
    o = io.StringIO()
    p = Printer(stream=o, **kwargs)
    return o,p
   
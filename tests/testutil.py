import io
from print_ext import Flattener

def printer(**kwargs):
    o = io.StringIO()
    p = Flattener(stream=o, **kwargs)
    return o,p
   
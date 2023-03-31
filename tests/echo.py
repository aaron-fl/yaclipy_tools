#!/usr/bin/env python
import sys
if __name__ == '__main__':
    for txt in sys.argv[2:]:
        stream, txt = (sys.stderr, txt[1:]) if txt.startswith('!') else (sys.stdout, txt)
        stream.write(txt+'\n')
        stream.flush()
    sys.exit(int(sys.argv[1]))

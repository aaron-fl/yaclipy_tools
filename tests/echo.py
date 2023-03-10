#!/usr/bin/env python
import sys
if __name__ == '__main__':
    sys.stdout.write(sys.argv[2]+'\n')
    sys.stderr.write(sys.argv[3]+'\n')
    sys.exit(int(sys.argv[1]))

#!/usr/bin/env python
import sys
sys.stdout.write(sys.argv[2]+'\n')
sys.stderr.write(sys.argv[3]+'\n')
sys.exit(int(sys.argv[1]))

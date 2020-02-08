#!/usr/bin/env python
import sys
from subprocess import Popen


filename = sys.argv[1]
config   = sys.argv[2]

while True:
    print('Starting ', filename)
    cmd = ['./ipcam.py', '--config_file', config]
    p = Popen(cmd)
    p.wait()


#!/usr/bin/env python
import sys
from subprocess import Popen

config   = sys.argv[1]

while True:
    cmd = ['./ipcam.py', '--config_file', config]
    p = Popen(cmd)
    p.wait()


#!/usr/bin/env python
import argparse
import sys
from subprocess import Popen

def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', type=str, required=True,
        help='absolute path to config file')
    ap.add_argument('--process', type=str, required=True,
        help='the process to run forever')

    return cli()

def main():
    args = cli()

    cmd = [sys.executable, args.process, '--config_file', args.config]
    p = Popen(cmd)
    p.wait()

if __name__ == '__main__':
    main()
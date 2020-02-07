#!/usr/bin/env python
import argparse
import json
import re
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

import cv2

from imcommon import ensure_directory_exists, save_tiff, start_frame
from imcommon import in_time_window


class CameraThreadConfig:
    def __init__(self, config_file):
        self.config_file    = config_file
        self.data           = self.parse_config()
        self.archive_exists = False

    def parse_config(self):
        with open(self.config_file, 'r') as f:
            s = f.read()
            return json.loads(s)

    def by_id(self, camera_id):
        for camera in self.data['cameras']:
            if camera['id'] == camera_id:
                return camera

    def n_cameras(self):
        return len(self.data['cameras'])


class CameraThread(threading.Thread):
    def __init__(self, config):
        super(CameraThread, self).__init__()
        self.config     = config
        self.camid      = config['id']
        self.addr       = config['url']
        self.archive    = config['archive']
        self.sleep      = config['sleep']
        self.start_hour = config['start']
        self.stop_hour  = config['stop']
        self.prefix     = start_frame(self.archive)
        self.nth_frame  = int(self.prefix)
        self.cap        = cv2.VideoCapture(self.addr)

        ensure_directory_exists(self.archive)

    def finish(self):
        self.cap.release()

    def capture(self):
        if self.cap.isOpened():
            ok, im = self.cap.read()
        else:
            print(f'[ERROR] opening video stream from {self.addr}')

        while True:
            if ok and in_time_window(self.start_hour, self.stop_hour):
                self.nth_frame += 1
                save_tiff(self.archive, im, prefix=str(self.nth_frame))
                ok, im = self.cap.read()

            time.sleep(self.sleep)

        self.finish()

    def run(self):
        self.running = True
        self.capture()


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config_file', type=str, required=True, help='path to a config file')
    return ap.parse_args()

def main(args):
    confs = CameraThreadConfig(args.config_file)
    ncams = confs.n_cameras()

    for i in range(ncams):
        config = confs.by_id(i)
        t      = CameraThread(config)
        t.start()

if __name__ == '__main__':
    args  = cli()
    main(args)

